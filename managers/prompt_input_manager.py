"""
Prompt input manager: reads prompts from TXT files. Supports:
- Prompts separated by "---" on its own line; each prompt can be multi-line and contain empty lines.
- If no "---" is found, the entire file is read as one prompt (empty lines preserved).

Automatically searches in prompts/ directory if file not found in current location.
"""
from pathlib import Path
from typing import List

from start_here.experiments.constants import PROMPTS_DIR

PROMPT_SEPARATOR = "---"

# Resolve prompts dir from this file so it works regardless of cwd (e.g. notebook in start_here/notebooks)
_PROMPTS_DIR_FROM_REPO = Path(__file__).resolve().parent.parent / "prompts"


def read_from_file(file_path: str, separator: str = PROMPT_SEPARATOR) -> List[str]:
    """Read prompts from a TXT file.

    - If the file contains a line with only the separator (e.g. "---"), the file
      is split by that separator; each block is one prompt (multi-line and empty
      lines allowed within each prompt).
    - If the separator never appears as a full line, the entire file is read as
      one prompt (empty lines preserved).

    If file is not found in the current location, searches in prompts/ directory.

    Args:
        file_path: Path to the TXT file (can be just filename if in prompts/)
        separator: Line used to separate prompts (default "---")

    Returns:
        List of prompts (leading/trailing whitespace trimmed per prompt; empty blocks skipped)
    """
    path = Path(file_path)

    if not path.exists():
        for base in (PROMPTS_DIR, _PROMPTS_DIR_FROM_REPO):
            candidate = base / path.name
            if candidate.exists():
                path = candidate
                break
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError(f"Only .txt files are supported. Found: {path.suffix}")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Multi-line mode: use separator only when it appears as a full line
    if any(line.strip() == separator for line in lines):
        prompts = []
        current = []
        for line in lines:
            if line.strip() == separator:
                if current:
                    prompts.append("\n".join(current).strip())
                    current = []
            else:
                current.append(line)
        if current:
            prompts.append("\n".join(current).strip())
        return [p for p in prompts if p]

    # No separator: entire file is one prompt (empty lines preserved)
    content = "\n".join(lines).strip()
    return [content] if content else []
