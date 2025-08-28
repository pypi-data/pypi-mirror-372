import os
import subprocess
from typing import Iterable, List, Optional, Tuple

import llm
from pydantic import Field


def _locate_acli_binary() -> str:
    """Return the CLI binary to call. Allow override via ACLI_BIN env var."""
    return os.environ.get("ACLI_BIN", "acli")


def _run_acli_rovodev(prompt: str, timeout: Optional[float] = 120.0) -> Tuple[int, str, str]:
    """Run `acli rovodev run <prompt>` and capture exit code, stdout, stderr.

    We pass the prompt as a single argument to avoid shell quoting issues.
    """
    cmd = [_locate_acli_binary(), "rovodev", "run", prompt]
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except FileNotFoundError as e:
        return 127, "", f"acli binary not found: {e}"
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", (e.stderr or "") + f"\nTimed out after {timeout}s"
    except Exception as e:  # Fallback safeguard
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
        parsed = None if opts.raw else _parse_response_block(stdout)
        content = stdout if (opts.raw or parsed is None) else parsed

        # Record metadata for observability
        response.response_json = {
            "provider": "acli rovodev",
            "model": model_name,
            "exit_code": exit_code,
            "raw_stdout_len": len(stdout),
            "stderr_len": len(stderr or ""),
            "parsed": parsed is not None and not opts.raw,
        }
        if stderr:
            response.response_json["stderr_preview"] = stderr[:4000]

        # If external command failed, surface a helpful message but still return any content we found
        if exit_code != 0 and not content:
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
