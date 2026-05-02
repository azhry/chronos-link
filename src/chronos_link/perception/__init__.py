"""Perception Layer — public API.

Provides :func:`probe`, the single entry-point that composes the
:class:`~chronos_link.perception.discovery.DiscoveryEngine` and the
:func:`~chronos_link.perception.constitution.load_constitution` loader into one call.
"""

from __future__ import annotations

from pathlib import Path

from chronos_link.perception.constitution import load_constitution
from chronos_link.perception.discovery import DiscoveryEngine
from chronos_link.perception.models import ProjectDNA


def probe(workspace: Path, *, max_depth: int | None = None) -> ProjectDNA:
    """Run the full Perception Layer probe on *workspace*.

    Parameters:
        workspace: Root directory to scan.
        max_depth: Optional depth limit forwarded to
            :class:`~chronos_link.perception.discovery.DiscoveryEngine`.

    Returns:
        A :class:`~chronos_link.perception.models.ProjectDNA` instance with detected
        stack signatures and the optional constitutional rules text.
    """
    engine = DiscoveryEngine(workspace, max_depth=max_depth)
    signatures = engine.scan()
    constitution = load_constitution(workspace)

    return ProjectDNA(
        root=workspace.resolve(),
        signatures=signatures,
        constitution=constitution,
    )
