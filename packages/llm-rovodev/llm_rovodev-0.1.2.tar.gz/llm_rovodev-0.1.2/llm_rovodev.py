import os
import sys
import logging
from typing import Iterable, List, Optional, Tuple

import click
import llm
from pydantic import Field

from llm_rovodev_debug import (
    LOGGER as _LOGGER,
    is_debug_enabled as _is_debug_enabled,
)

# Modularized helpers
from llm_rovodev_cli import run_acli_rovodev
from llm_rovodev_parser import (
    extract_model,
    detect_ai_policy_filter,
    parse_all_response_blocks,
)
from llm_rovodev_prompt import (
    prepare_message_args_from_prompt,
)

class RovoDev(llm.Model):
    model_id = "rovodev"
    can_stream = True

    class Options(llm.Options):
        raw: bool = Field(
            default=False,
            description="If true, return raw stdout from 'acli rovodev run' without parsing the Response block.",
        )
        timeout_seconds: float = Field(
            default=600.0,
            description="Timeout in seconds for the external 'acli rovodev run' process (default 600s).",
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
        # Build full prompt including any fragments provided with -f
        def _safe_fragment_to_text(frag) -> Optional[str]:
            # Try common attributes used by LLM fragments
            for attr in ("content", "text", "value"):
                try:
                    v = getattr(frag, attr, None)
                except Exception:
                    v = None
                if isinstance(v, str) and v:
                    return v
            # Fallback: str(frag) if it looks like text
            try:
                s = str(frag)
                # Heuristic: avoid noisy reprs
                if isinstance(s, str) and len(s) > 0 and not s.startswith("<"):
                    return s
            except Exception:
                pass
            return None

        fragments_text: List[str] = []
        try:
            frags = getattr(prompt, "fragments", None)
        except Exception:
            frags = None
        if isinstance(frags, (list, tuple)):
            for f in frags:
                t = _safe_fragment_to_text(f)
                if t:
                    fragments_text.append(t)
        # Deduplicate identical fragment texts while preserving order
        if fragments_text:
            seen = set()
            deduped: List[str] = []
            for t in fragments_text:
                key = "\n".join(t.splitlines()).strip()
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(t)
            fragments_text = deduped

        base_text: str = (getattr(prompt, "prompt", None) or "")
        if fragments_text:
            user_text = "\n\n".join(fragments_text + ([base_text] if base_text else []))
        else:
            user_text = base_text

        opts: RovoDev.Options = prompt.options or RovoDev.Options()

        # Prepare message args, possibly writing a long prompt to a dot temp file
        message_args, dot_file = prepare_message_args_from_prompt(user_text)

        # Use user-configurable timeout; default is 600s, minimum 120s
        _t = float(opts.timeout_seconds or 600.0)
        if _t < 120.0:
            _t = 120.0
        exit_code, stdout, stderr = run_acli_rovodev(message_args, timeout=_t)

        model_name = extract_model(stdout)

        # Detect Atlassian AI Policy Filter blocks before parsing normal response
        ai_filter = detect_ai_policy_filter(stdout)
        if ai_filter:
            raise click.ClickException(
                "Your prompt was blocked by the Atlassian AI policy filter. "
                "Try rephrasing and trying again. Details:\n" + ai_filter
            )

        # Always attempt to parse all Response blocks and join them
        parsed_blocks = parse_all_response_blocks(stdout)
        parsed = "\n\n".join(parsed_blocks) if parsed_blocks else None
        if parsed is None:
            # No model response found; optionally log details in debug mode
            if _is_debug_enabled():
                _LOGGER.debug("No Response block found in rovodev CLI output; stdout_len=%d stderr_len=%d", len(stdout or ""), len(stderr or ""))
                try:
                    from llm_rovodev_debug import STDIO_LOGGER as _STDIO_LOGGER
                except Exception:
                    _STDIO_LOGGER = _LOGGER
                _STDIO_LOGGER.debug("stdout (full):\n%s", stdout or "")
                _STDIO_LOGGER.debug("stderr (full):\n%s", stderr or "")
            # Raise a clear error with hint for users
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
        if dot_file:
            # Include the dot-file name so users can inspect or clean it up
            response.response_json["dot_prompt_file"] = dot_file

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
