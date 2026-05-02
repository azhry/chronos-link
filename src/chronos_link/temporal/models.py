"""Temporal Layer data models.

Defines value objects for git-derived architectural deltas and the
K-window ADR context used by the Synthesis Layer.
"""

from __future__ import annotations

from pydantic import BaseModel


class ArchitecturalSignal(BaseModel):
    """A single architecture-relevant keyword detected in a commit message.

    Attributes:
        keyword: The matched signal keyword (e.g. "Refactor", "Migrate").
        source: The raw commit message fragment that triggered the match.
    """

    keyword: str
    source: str


def truncate_diff(diff: str, max_chars: int = 2000) -> str:
    """Truncate a diff if it exceeds max_chars."""
    if len(diff) <= max_chars:
        return diff
    return diff[:max_chars] + f"\n... [Truncated {len(diff) - max_chars} characters for brevity] ..."


class ArchitecturalDelta(BaseModel):
    """The current code change context extracted from Git.

    Attributes:
        staged_diff: Output of ``git diff --cached`` (empty if nothing staged).
        last_commit_diff: Output of ``git log -p -n 1`` for the latest commit.
        last_commit_message: The commit message of the most recent commit.
        signals: Architecture-relevant keywords found in the commit message.
    """

    staged_diff: str = ""
    last_commit_diff: str = ""
    last_commit_message: str = ""
    signals: list[ArchitecturalSignal] = []

    def truncate(self, max_chars: int = 2000) -> None:
        """Truncate large diffs in place."""
        self.staged_diff = truncate_diff(self.staged_diff, max_chars)
        self.last_commit_diff = truncate_diff(self.last_commit_diff, max_chars)


class ADREntry(BaseModel):
    """A parsed existing ADR from the ``docs/adr/`` directory.

    Attributes:
        id: Zero-padded ADR identifier (e.g. ``"0003"``).
        title: The ADR title extracted from the ``# ADR ...`` heading.
        filename: Original filename on disk.
        status: Status string (Proposed, Accepted, Superseded, Deprecated).
        context: Raw text of the Context section.
        decision: Raw text of the Decision section.
        consequences: Raw text of the Consequences section.
    """

    id: str
    title: str
    filename: str
    status: str = ""
    context: str = ""
    decision: str = ""
    consequences: str = ""


class TemporalContext(BaseModel):
    """Aggregated temporal context passed to the Synthesis Layer.

    Attributes:
        delta: The architectural delta from the current Git state.
        historical_adrs: The last *K* ADRs (most recent last).
        k: The window size used.
    """

    delta: ArchitecturalDelta
    historical_adrs: list[ADREntry] = []
    k: int = 5
