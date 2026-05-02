"""ADRReader — parses existing ADR files for the K-window context.

Scans the ADR output directory for ``*.md`` files whose filenames start
with a zero-padded numeric ID (e.g. ``0003-use-grpc.md``), extracts the
standard Nygard sections, and returns the last *K* entries.
"""

from __future__ import annotations

import re
from pathlib import Path

from chronos_link.temporal.models import ADREntry

# Pattern to extract the zero-padded ID from a filename like "0003-foo.md".
_ID_PATTERN: re.Pattern[str] = re.compile(r"^(\d{4,})")

# Section heading pattern (## SectionName)
_SECTION_HEADING: re.Pattern[str] = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def _parse_sections(text: str) -> dict[str, str]:
    """Split an ADR markdown file into its ``## Section`` blocks.

    Returns a dict keyed by **lowercased** section name, values are the
    raw body text of each section (leading/trailing whitespace stripped).
    """
    headings = list(_SECTION_HEADING.finditer(text))
    sections: dict[str, str] = {}
    for idx, match in enumerate(headings):
        name = match.group(1).strip().lower()
        start = match.end()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        sections[name] = text[start:end].strip()
    return sections


def _parse_title(text: str) -> str:
    """Extract the ADR title from the ``# ADR NNNN: Title`` heading."""
    m = re.search(r"^#\s+ADR\s+\d+:\s*(.+)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Fallback: first H1 heading
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


class ADRReader:
    """Reads and parses ADR files from an output directory.

    Parameters:
        adr_dir: Path to the directory containing ADR markdown files.
    """

    def __init__(self, adr_dir: Path) -> None:
        self.adr_dir = adr_dir

    def read_all(self) -> list[ADREntry]:
        """Read and parse all ADR files, sorted by ID ascending.

        Files that do not start with a numeric ID prefix are silently
        skipped.
        """
        if not self.adr_dir.is_dir():
            return []

        entries: list[ADREntry] = []
        for filepath in sorted(self.adr_dir.glob("*.md")):
            id_match = _ID_PATTERN.match(filepath.stem)
            if not id_match:
                continue

            adr_id = id_match.group(1)
            try:
                text = filepath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            title = _parse_title(text)
            sections = _parse_sections(text)

            entries.append(
                ADREntry(
                    id=adr_id,
                    title=title,
                    filename=filepath.name,
                    status=sections.get("status", ""),
                    context=sections.get("context", ""),
                    decision=sections.get("decision", ""),
                    consequences=sections.get("consequences", ""),
                )
            )

        return entries

    def read_last_k(self, k: int = 5) -> list[ADREntry]:
        """Return the last *k* ADRs by ID (most recent last).

        Parameters:
            k: Number of ADRs to return (the K-window).
        """
        all_entries = self.read_all()
        return all_entries[-k:] if len(all_entries) > k else all_entries
