"""GitWrapper — programmatic access to Git diffs, logs, and signal extraction.

Uses *GitPython* to interact with the repository at the workspace root.
Provides methods aligned with SPEC.md Section 2.2 (Temporal Layer).
"""

from __future__ import annotations

import re
from pathlib import Path

from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError

from chronos_link.temporal.models import ArchitecturalDelta, ArchitecturalSignal

# ---------------------------------------------------------------------------
# Architecture signal keywords (case-insensitive matching)
# ---------------------------------------------------------------------------
_SIGNAL_KEYWORDS: list[str] = [
    "Refactor",
    "Migrate",
    "Trade-off",
    "Tradeoff",
    "Breaking",
    "Deprecate",
    "Deprecated",
    "Replace",
    "Remove",
    "Introduce",
    "Adopt",
    "Split",
    "Merge",
    "Extract",
    "Decouple",
    "Consolidate",
]

# Pre-compiled pattern: match any keyword as a whole word (case-insensitive).
_SIGNAL_PATTERN: re.Pattern[str] = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _SIGNAL_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


class GitWrapper:
    """Wraps Git operations for a single workspace repository.

    Parameters:
        workspace: Path to the repository root.

    Raises:
        InvalidGitRepositoryError: If *workspace* is not inside a Git repo.
    """

    def __init__(self, workspace: Path) -> None:
        self.repo = Repo(workspace, search_parent_directories=True)

    # -- Public API ----------------------------------------------------------

    def get_staged_diff(self) -> str:
        """Return the output of ``git diff --cached``.

        Returns an empty string when nothing is staged.
        """
        try:
            return self.repo.git.diff("--cached")
        except GitCommandError:
            return ""

    def get_last_commit_diff(self) -> str:
        """Return the patch of the most recent commit (``git log -p -n 1``).

        Returns an empty string when the repo has no commits.
        """
        try:
            return self.repo.git.log("-p", "-n", "1")
        except GitCommandError:
            return ""

    def get_last_commit_message(self) -> str:
        """Return the commit message of HEAD.

        Returns an empty string when the repo has no commits.
        """
        try:
            return self.repo.head.commit.message.strip()
        except (ValueError, TypeError):
            return ""

    @staticmethod
    def extract_signals(message: str) -> list[ArchitecturalSignal]:
        """Detect architecture-relevant keywords in a commit message.

        Parameters:
            message: The raw commit message text.

        Returns:
            A list of :class:`ArchitecturalSignal` instances for each match.
        """
        signals: list[ArchitecturalSignal] = []
        seen: set[str] = set()
        for match in _SIGNAL_PATTERN.finditer(message):
            keyword = match.group(1)
            normalised = keyword.lower()
            if normalised not in seen:
                seen.add(normalised)
                signals.append(
                    ArchitecturalSignal(keyword=keyword, source=message)
                )
        return signals

    def build_delta(self) -> ArchitecturalDelta:
        """Construct the full :class:`ArchitecturalDelta` for this repo."""
        staged = self.get_staged_diff()
        last_diff = self.get_last_commit_diff()
        last_msg = self.get_last_commit_message()
        signals = self.extract_signals(last_msg)

        delta = ArchitecturalDelta(
            staged_diff=staged,
            last_commit_diff=last_diff,
            last_commit_message=last_msg,
            signals=signals,
        )
        delta.truncate()
        return delta
