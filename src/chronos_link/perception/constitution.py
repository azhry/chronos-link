"""Constitution loader — reads the project's architectural rules.

Searches for ``.adr-rules`` or ``PROMPT.md`` at the workspace root and
returns the raw constitution text.
"""

from __future__ import annotations

from pathlib import Path

# File names recognised as a project constitution (checked in order).
_CONSTITUTION_FILES: list[str] = [
    "docs/adr/CONSTITUTION.md",
    "CONSTITUTION.md",
    ".adr-rules",
    "PROMPT.md",
]


def load_constitution(root: Path) -> str | None:
    """Load the architectural constitution from the workspace root.

    Parameters:
        root: Workspace root directory.

    Returns:
        The raw text content of the constitution file, or ``None`` if no
        constitution file exists.
    """
    for name in _CONSTITUTION_FILES:
        candidate = root / name
        if candidate.is_file():
            try:
                return candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
    return None
