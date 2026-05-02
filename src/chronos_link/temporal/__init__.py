"""Temporal Layer — context retrieval.

Composes the GitWrapper and ADRReader to provide the full temporal
context (delta + K-window history) to the Synthesis Layer.
"""

from __future__ import annotations

from pathlib import Path

from chronos_link.temporal.adr_reader import ADRReader
from chronos_link.temporal.git_wrapper import GitWrapper
from chronos_link.temporal.models import TemporalContext


def retrieve_context(
    workspace: Path,
    adr_dir: Path,
    k: int = 5,
) -> TemporalContext:
    """Retrieve the full temporal context for the given workspace.

    Parameters:
        workspace: Root directory of the Git repository.
        adr_dir: Directory containing existing ADR files.
        k: Number of historical ADRs to retrieve.

    Returns:
        A :class:`~chronos_link.temporal.models.TemporalContext` instance.
    """
    # 1. Extract architectural delta from Git
    try:
        git = GitWrapper(workspace)
        delta = git.build_delta()
    except Exception:
        # Fallback for non-git environments or errors
        from chronos_link.temporal.models import ArchitecturalDelta
        delta = ArchitecturalDelta()

    # 2. Retrieve last K ADRs
    reader = ADRReader(adr_dir)
    history = reader.read_last_k(k)

    return TemporalContext(
        delta=delta,
        historical_adrs=history,
        k=k,
    )
