"""End-to-End Smoke Test for the Chronos-Link-V1 CLI."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from chronos_link.main import app

runner = CliRunner()


@pytest.fixture()
def mock_env(tmp_path):
    """Setup a mock project environment."""
    # Create go.mod
    (tmp_path / "go.mod").write_text("module test", encoding="utf-8")
    
    # Create existing ADRs
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-existing.md").write_text("# ADR 0001", encoding="utf-8")
    
    return tmp_path


from unittest.mock import MagicMock, patch, AsyncMock
from chronos_link.config import settings

@patch("chronos_link.diagramming.mermaid.get_llm")
@patch("chronos_link.synthesis.nodes.get_llm")
def test_cli_generate_full_pipeline(mock_get_llm, mock_mermaid_get_llm, git_repo) -> None:
    """The CLI should run all 4 phases and save a file."""
    
    # Satisfy Pydantic validation for ChatGoogleGenerativeAI
    settings.gemini_api_key = "dummy-key"

    # Setup mock env
    adr_dir = git_repo / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-existing.md").write_text("# ADR 0001", encoding="utf-8")
    (git_repo / "go.mod").write_text("module test", encoding="utf-8")

    # Mock LLM Responses
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock()
    mock_get_llm.return_value = mock_llm
    mock_mermaid_get_llm.return_value = mock_llm
    
    mock_llm.ainvoke.side_effect = [
        MagicMock(content="## Draft"),  # Actor
        MagicMock(content="VALID"),      # Critic
        MagicMock(content="# ADR 0002: Decision\nSuccess"), # Polisher
        MagicMock(content="NONE")        # Mermaid generator
    ]
    
    # Execute CLI
    result = runner.invoke(app, ["--workspace", str(git_repo)])
    
    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

    # Assertions
    assert result.exit_code == 0
    assert "[1/4] Probing environment" in result.stdout
    assert "[4/4] Synthesizing ADR" in result.stdout
    assert "[SUCCESS] ADR saved to" in result.stdout
    
    # Check if file exists
    expected_file = adr_dir / "0002-architectural-decision.md"
    assert expected_file.exists()
    assert "Success" in expected_file.read_text()
