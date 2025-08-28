from typing import List, Optional


def extract_model(stdout: str) -> Optional[str]:
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("Using model:"):
            return line.split(":", 1)[1].strip()
    return None


def extract_box_content(stdout: str, title_substring: str) -> Optional[str]:
    """Extract inner content from a box whose header line contains title_substring.

    The box format uses Unicode box drawing characters similar to "╭─ Title ─╮".
    """
    if title_substring not in stdout:
        return None
    lines = stdout.splitlines()
    in_block = False
    content: List[str] = []
    for raw in lines:
        line = raw.rstrip("\n")
        if not in_block:
            start = line.strip().startswith("╭") and (title_substring in line)
            if start:
                in_block = True
            continue
        stripped = line.strip()
        if stripped.startswith("╰"):
            break
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
        content.append(stripped)
    if not content:
        return None
    while content and not content[0].strip():
        content.pop(0)
    while content and not content[-1].strip():
        content.pop()
    return "\n".join(content)


def detect_ai_policy_filter(stdout: str) -> Optional[str]:
    """Return the inner content of an AI Policy Filter box if present."""
    return extract_box_content(stdout, "AI Policy Filter")


def parse_all_response_blocks(stdout: str) -> List[str]:
    """Extract inner content for all box-drawn "Response" sections.

    Returns a list of strings, one per Response block, in order of appearance.
    """
    lines = stdout.splitlines()
    i = 0
    blocks: List[str] = []
    n = len(lines)

    while i < n:
        line = lines[i].rstrip("\n")
        if line.strip().startswith("╭") and ("Response" in line):
            # Parse a single block
            i += 1
            content: List[str] = []
            while i < n:
                l2 = lines[i].rstrip("\n")
                s2 = l2.strip()
                if s2.startswith("╰"):
                    # End of this block
                    break
                if "│" in l2:
                    try:
                        left = l2.index("│")
                        right = l2.rindex("│")
                        if right > left:
                            inner = l2[left + 1 : right]
                            content.append(inner.strip())
                        else:
                            content.append(s2)
                    except ValueError:
                        content.append(s2)
                else:
                    content.append(s2)
                i += 1
            # Normalize content
            while content and not content[0].strip():
                content.pop(0)
            while content and not content[-1].strip():
                content.pop()
            if content:
                blocks.append("\n".join(content))
            # Advance past the closing line if present
            if i < n:
                i += 1
            continue
        i += 1
    return blocks
