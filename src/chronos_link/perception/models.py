"""Perception layer data models.

Defines the core value objects produced by the environmental probing stage.
"""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class StackType(str, Enum):
    """Technology stack categories detected via manifest scanning."""

    GO = "go"
    NODE = "node"
    PYTHON = "python"
    DOTNET = "dotnet"
    DOCKER = "docker"
    DOCKER_COMPOSE = "docker-compose"
    HELM = "helm"
    TERRAFORM = "terraform"
    KUBERNETES = "kubernetes"
    CAPI = "cluster-api"
    UNKNOWN = "unknown"


class StackSignature(BaseModel):
    """A single detected technology stack indicator.

    Attributes:
        manifest_path: Absolute path to the manifest file or directory that
            triggered detection (e.g. ``/repo/go.mod``).
        stack_type: The categorised technology stack.
        context: Optional extra context extracted from the manifest
            (e.g. Go module name, Node package name).
    """

    manifest_path: Path
    stack_type: StackType
    context: str = ""


class ProjectDNA(BaseModel):
    """Aggregated result of the Perception Layer probe.

    Attributes:
        root: Workspace root that was scanned.
        signatures: All detected stack signatures.
        constitution: Raw text of the architectural constitution file
            (``.adr-rules`` or ``PROMPT.md``), or *None* if absent.
    """

    root: Path
    signatures: list[StackSignature]
    constitution: str | None = None
