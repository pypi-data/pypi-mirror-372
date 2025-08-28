import os
import subprocess
import time
from typing import Callable, List, Optional, Tuple

from llm_rovodev_debug import (
    LOGGER as _LOGGER,
    ensure_logger_configured as _ensure_logger_configured,
    is_debug_enabled as _is_debug_enabled,
    redacted_environ as _redacted_environ,
)


def locate_acli_binary() -> str:
    """Return the CLI binary to call. Allow override via ACLI_BIN env var."""
    return os.environ.get("ACLI_BIN", "acli")


def run_acli_rovodev(
    message_args: List[str],
    timeout: Optional[float] = 120.0,
    on_spawn: Optional[Callable[["subprocess.Popen[str]"], None]] = None,
) -> Tuple[int, str, str]:
    """Run `acli rovodev run <MESSAGE>...` with one or more message arguments.

    We avoid shell=True and pass args as a list to preserve whitespace safely.
    """
    _ensure_logger_configured()
    cmd = [locate_acli_binary(), "rovodev", "run", *message_args]

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
        # Show the primary message explicitly too
        if message_args:
            _LOGGER.debug("llm->subprocess primary message (verbatim)=%r", message_args[0])

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
            _LOGGER.debug("stdout_len=%d", len(completed.stdout or ""))
            _LOGGER.debug("stderr_len=%d", len(completed.stderr or ""))
            # For successful runs, avoid logging full stdout/stderr to prevent
            # leaking banners into normal output in test harnesses that merge streams.
            # If the subprocess failed, include full stdio to aid debugging.
            if completed.returncode != 0:
                try:
                    from llm_rovodev_debug import STDIO_LOGGER as _STDIO_LOGGER
                except Exception:
                    _STDIO_LOGGER = _LOGGER
                _STDIO_LOGGER.debug("stdout (full):\n%s", completed.stdout or "")
                _STDIO_LOGGER.debug("stderr (full):\n%s", completed.stderr or "")
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
