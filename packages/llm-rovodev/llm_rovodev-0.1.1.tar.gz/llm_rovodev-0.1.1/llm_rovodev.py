import os
import subprocess
import sys
import time
import logging
from typing import Iterable, List, Optional, Tuple, Dict

import click
import llm
from pydantic import Field

from llm_rovodev_debug import (
    LOGGER as _LOGGER,
    ensure_logger_configured as _ensure_logger_configured,
    is_debug_enabled as _is_debug_enabled,
    redacted_environ as _redacted_environ,
)




def _locate_acli_binary() -> str:
    """Return the CLI binary to call. Allow override via ACLI_BIN env var."""
    return os.environ.get("ACLI_BIN", "acli")


def _run_acli_rovodev(prompt: str, timeout: Optional[float] = 120.0) -> Tuple[int, str, str]:
    """Run `acli rovodev run <prompt>` and capture exit code, stdout, stderr.

    We pass the prompt as a single argument to avoid shell quoting issues.
    """
    _ensure_logger_configured()
    cmd = [_locate_acli_binary(), "rovodev", "run", prompt]

    # Debug: show full invocation context
    if _is_debug_enabled():
        _LOGGER.debug("About to spawn subprocess")
        _LOGGER.debug("cwd=%s", os.getcwd())
        _LOGGER.debug("timeout=%s", timeout)
        _LOGGER.debug("command(list)=%r", cmd)
        # For readability, also show a shell-quoted string
        try:
            import shlex

            _LOGGER.debug("command(shlex)=%s", " ".join(shlex.quote(s) for s in cmd))
        except Exception:
            pass
        # Include a redacted view of environment
        _LOGGER.debug("env(redacted)=%r", _redacted_environ())
        # Show the prompt explicitly too (it is already in cmd but easier to see here)
        _LOGGER.debug("llm->subprocess prompt (verbatim)=%r", prompt)

    start = time.time()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration = time.time() - start
        if _is_debug_enabled():
            _LOGGER.debug("subprocess finished rc=%s in %.3fs", completed.returncode, duration)
            # Avoid dumping full stdout/stderr to not leak banner content into output captures
            _LOGGER.debug("stdout_len=%d", len(completed.stdout or ""))
            _LOGGER.debug("stderr_len=%d", len(completed.stderr or ""))
        return completed.returncode, completed.stdout, completed.stderr
    except FileNotFoundError as e:
        if _is_debug_enabled():
            _LOGGER.exception("acli binary not found")
        return 127, "", f"acli binary not found: {e}"
    except subprocess.TimeoutExpired as e:
        if _is_debug_enabled():
            _LOGGER.exception("subprocess timed out after %ss", timeout)
        return 124, e.stdout or "", (e.stderr or "") + f"\nTimed out after {timeout}s"
    except Exception as e:  # Fallback safeguard
        if _is_debug_enabled():
            _LOGGER.exception("unexpected error invoking acli: %s", e)
        return 1, "", f"Unexpected error invoking acli: {e}"


def _extract_model(stdout: str) -> Optional[str]:
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("Using model:"):
            return line.split(":", 1)[1].strip()
    return None


def _parse_response_block(stdout: str) -> Optional[str]:
    """Extract the text inside the box-drawn "Response" section from acli output.

    Looks for a line that includes 'Response' and starts with the box-drawing top-left corner.
    Then collects subsequent lines that start with a vertical box char, trimming the borders,
    until the closing border line is encountered.

    Returns None if a response block could not be identified.
    """
    lines = stdout.splitlines()
    in_block = False
    content: List[str] = []

    for raw in lines:
        line = raw.rstrip("\n")
        if not in_block:
            # Try to detect the start of the Response block
            # Common pattern: "╭─ Response ...╮"
            start = line.strip().startswith("╭") and ("Response" in line)
            if start:
                in_block = True
            continue
        # If we are in the block, stop at the closing border line
        stripped = line.strip()
        if stripped.startswith("╰"):
            break
        # Extract text between vertical borders: "│ ... │"
        if "│" in line:
            try:
                left = line.index("│")
                right = line.rindex("│")
                if right > left:
                    inner = line[left + 1 : right]
                    content.append(inner.strip())
                    continue
            except ValueError:
                pass
        # Fallback: if no borders found, treat as plain content
        content.append(stripped)

    if not content:
        return None
    # Normalize trailing whitespace and blank lines
    # Keep intentional blank lines present in content
    # Strip leading/trailing empty lines
    while content and not content[0].strip():
        content.pop(0)
    while content and not content[-1].strip():
        content.pop()
    return "\n".join(content)


class RovoDev(llm.Model):
    model_id = "rovodev"
    can_stream = True

    class Options(llm.Options):
        raw: bool = Field(
            default=False,
            description="If true, return raw stdout from 'acli rovodev run' without parsing the Response block.",
        )

    def execute(
        self,
        prompt,  # llm.Prompt
        stream: bool,
        response,  # llm.Response
        conversation,  # llm.Conversation | None
    ) -> Iterable[str]:
        """Execute the prompt by invoking the external 'acli rovodev run' CLI.

        We capture stdout/stderr, parse the 'Response' content block, and stream or return it.
        When streaming is enabled, we emit line-by-line (with optional delay).
        """
        user_text: str = prompt.prompt or ""
        opts: RovoDev.Options = prompt.options or RovoDev.Options()

        # Use a sensible internal default timeout, not user-configurable
        exit_code, stdout, stderr = _run_acli_rovodev(user_text, timeout=120.0)

        model_name = _extract_model(stdout)

        # Always attempt to parse a Response block first
        parsed = _parse_response_block(stdout)
        if parsed is None:
            # No model response found; raise a clear error
            # Include a hint for users on how to inspect full raw output
            raise click.ClickException(
                "No Response block found in rovodev CLI output. "
                "Enable LLM_ROVODEV_DEBUG=1 to capture full logs or run the rovodev CLI directly to debug."
            )

        # If a Response block exists, choose output based on raw option
        content = stdout if opts.raw else parsed

        # Record metadata for observability
        response.response_json = {
            "provider": "acli rovodev",
            "model": model_name,
            "exit_code": exit_code,
            "raw_stdout_len": len(stdout),
            "stderr_len": len(stderr or ""),
            "parsed": True,
        }
        if stderr:
            response.response_json["stderr_preview"] = stderr[:4000]

        # If external command failed and no content was produced in raw mode, surface a helpful message
        if opts.raw and exit_code != 0 and not content:
            msg = stderr.strip() or f"'acli rovodev run' failed with exit code {exit_code}"
            content = f"Error from rovodev CLI: {msg}"

        # Stream or return full content
        if stream:
            for line in content.splitlines(True):  # keepends True to preserve newlines
                yield line
        else:
            yield content


@llm.hookimpl
def register_models(register):
    register(RovoDev())
