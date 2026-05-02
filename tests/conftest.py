"""Shared pytest fixtures for DAKE tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace directory and return its path."""
    return tmp_path


@pytest.fixture()
def go_workspace(tmp_path: Path) -> Path:
    """Workspace containing a Go project (go.mod + Dockerfile)."""
    (tmp_path / "go.mod").write_text(
        "module github.com/example/myservice\n\ngo 1.22\n\n"
        "require (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
        encoding="utf-8",
    )
    (tmp_path / "Dockerfile").write_text(
        "FROM golang:1.22-alpine\nWORKDIR /app\nCOPY . .\nRUN go build -o server .\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def monorepo_workspace(tmp_path: Path) -> Path:
    """Workspace simulating a monorepo with Go, Node, and Terraform."""
    # Go service
    svc = tmp_path / "services" / "api"
    svc.mkdir(parents=True)
    (svc / "go.mod").write_text(
        "module github.com/mono/api\n\ngo 1.22\n", encoding="utf-8"
    )

    # Node frontend
    web = tmp_path / "web"
    web.mkdir()
    (web / "package.json").write_text(
        '{"name": "mono-web", "version": "1.0.0"}', encoding="utf-8"
    )

    # Terraform infra
    infra = tmp_path / "infra"
    infra.mkdir()
    (infra / "main.tf").write_text(
        'provider "aws" {\n  region = "us-east-1"\n}\n', encoding="utf-8"
    )

    # Helm charts
    charts = tmp_path / "charts"
    charts.mkdir()
    (charts / "Chart.yaml").write_text(
        "apiVersion: v2\nname: mono\nversion: 0.1.0\n", encoding="utf-8"
    )

    return tmp_path


@pytest.fixture()
def constitution_workspace(tmp_path: Path) -> Path:
    """Workspace with a .adr-rules constitution file."""
    (tmp_path / ".adr-rules").write_text(
        "Always use Hexagonal Architecture\n"
        "No direct database access from the UI\n"
        "All services must expose gRPC endpoints\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def sample_adr_dir(tmp_path: Path) -> Path:
    """Create 7 sample ADR files for K-window testing."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    for i in range(1, 8):
        content = (
            f"# ADR {i:04d}: Sample Decision {i}\n\n"
            f"## Status\nAccepted\n\n"
            f"## Context\nSample context for ADR {i:04d}.\n\n"
            f"## Decision\nWe decided to do thing {i}.\n\n"
            f"## Consequences\n"
            f"* **Performance:** Neutral\n"
            f"* **Scalability:** Positive\n"
            f"* **Maintainability:** Positive\n"
            f"* **Cost:** Neutral\n"
        )
        (adr_dir / f"{i:04d}-sample-decision-{i}.md").write_text(
            content, encoding="utf-8"
        )

    return adr_dir


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository with some history."""
    from git import Repo
    repo = Repo.init(tmp_path)
    
    # Create an initial commit
    file1 = tmp_path / "README.md"
    file1.write_text("Initial content", encoding="utf-8")
    repo.index.add([str(file1)])
    repo.index.commit("Initial commit")
    
    return tmp_path
