import os
import time
from typing import Iterable, List, Optional, Tuple

MAX_INLINE_CHARS = 256
DOT_PREFIX = ".llm_rovodev_prompt_"

def create_dot_temp_prompt_file(content: str) -> str:
    """Create a temp file in CWD named ./.llm_rovodev_prompt_<ts>.txt with the provided content.
    Returns the relative path (e.g. ".llm_rovodev_prompt_1234.txt").
    """
    ts = int(time.time() * 1000)
    base_name = f"{DOT_PREFIX}{ts}"
    suffix = ".txt"
    fname = base_name + suffix
    n = 0
    while os.path.exists(fname):
        n += 1
        fname = f"{base_name}_{n}{suffix}"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)
    return fname


def prepare_message_args_from_prompt(prompt: str) -> Tuple[List[str], Optional[str]]:
    """Return message args for `acli rovodev run`.

    - If prompt <= MAX_INLINE_CHARS, send it as a single argument.
    - If longer, write it to a dot temp file in cwd and send a short instruction
      telling the agent to open and follow that file.
    """
    if prompt is None:
        prompt = ""
    if len(prompt) <= MAX_INLINE_CHARS:
        return [prompt], None
    # Long prompt: store to file and instruct agent to open it
    fname = create_dot_temp_prompt_file(prompt)
    # Use explicit 'Open ./<file>' phrasing so agents can call tools on it
    if fname.startswith("./"):
        path_display = fname
    elif fname.startswith("."):
        path_display = f"./{fname}"
    else:
        path_display = f"./{fname}"
    instruction = (
        f"Open {path_display} to read the notes before answering."
    )
    return [instruction], fname


def iter_existing_dot_prompts() -> Iterable[str]:
    for name in os.listdir("."):
        if name.startswith(DOT_PREFIX):
            yield name


def delete_old_dot_prompts(exclude: Optional[str] = None) -> int:
    """Delete existing dot prompt files, optionally excluding a specific file.

    Returns the count of deleted files.
    """
    deleted = 0
    for path in list(iter_existing_dot_prompts()):
        if exclude and os.path.abspath(path) == os.path.abspath(exclude):
            continue
        try:
            os.remove(path)
            deleted += 1
        except FileNotFoundError:
            continue
        except Exception:
            # Best-effort cleanup; ignore errors
            continue
    return deleted
