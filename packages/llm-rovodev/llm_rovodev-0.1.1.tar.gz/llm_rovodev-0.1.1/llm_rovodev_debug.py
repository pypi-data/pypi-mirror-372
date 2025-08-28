import logging
import os
import sys
from typing import Dict

_DEBUG_ENV_VAR = "LLM_ROVODEV_DEBUG"

# Shared logger for the plugin
LOGGER = logging.getLogger("llm_rovodev")
LOGGER.setLevel(logging.INFO)


def is_truthy_env(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in {"1", "true", "yes", "on", "debug"}


def is_debug_enabled() -> bool:
    return is_truthy_env(_DEBUG_ENV_VAR)


def ensure_logger_configured() -> None:
    """Attach a stream handler to LOGGER when debug is enabled.

    - If stdout is redirected (non-tty), emit logs to stdout so users can redirect `>` and capture logs.
    - Otherwise, emit logs to stderr.
    - Avoid attaching duplicate handlers to the same stream.
    """
    if not is_debug_enabled():
        return

    try:
        stdout_is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    except Exception:
        stdout_is_tty = True
    stream = sys.stdout if not stdout_is_tty else sys.stderr

    for h in LOGGER.handlers:
        if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is stream:
            return

    handler = logging.StreamHandler(stream=stream)
    fmt = "[llm-rovodev] %(levelname)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(logging.DEBUG)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.DEBUG)


def _mask_value(key: str, value: str) -> str:
    key_u = key.upper()
    sensitive = (
        key_u.endswith("_KEY")
        or key_u.endswith("_TOKEN")
        or key_u.endswith("_SECRET")
        or key_u in {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "AZURE_OPENAI_API_KEY", "LLM_API_KEY"}
    )
    if sensitive and value:
        return value[:2] + "…" if len(value) > 2 else "…"
    return value


def redacted_environ() -> Dict[str, str]:
    try:
        env = dict(os.environ)
    except Exception:
        return {}
    redacted = {}
    for k, v in env.items():
        if not isinstance(v, str):
            v = str(v)
        redacted[k] = _mask_value(k, v)
    return redacted
