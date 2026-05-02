"""Tests for the Synthesis Layer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from chronos_link.perception.models import ProjectDNA
from chronos_link.temporal.models import TemporalContext, ArchitecturalDelta
from chronos_link.synthesis.graph import synthesis_engine


@pytest.fixture()
def mock_dna(tmp_path) -> ProjectDNA:
    return ProjectDNA(root=tmp_path, signatures=[])


@pytest.fixture()
def mock_temporal() -> TemporalContext:
    return TemporalContext(delta=ArchitecturalDelta())


@pytest.mark.asyncio
async def test_graph_compilation() -> None:
    """The LangGraph instance should be correctly compiled."""
    assert synthesis_engine is not None


@pytest.mark.asyncio
@patch("chronos_link.diagramming.mermaid.get_llm")
@patch("chronos_link.synthesis.nodes.get_llm")
async def test_full_run_mocked(mock_get_llm, mock_mermaid_get_llm, mock_dna, mock_temporal) -> None:
    """Test a full graph execution with mocked LLM responses."""
    
    # Setup mock responses
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock()
    mock_get_llm.return_value = mock_llm
    mock_mermaid_get_llm.return_value = mock_llm
    
    # 1. Actor response
    actor_resp = MagicMock()
    actor_resp.content = "## ADR Draft\nThis is a draft."
    
    # 2. Critic response (valid)
    critic_resp = MagicMock()
    critic_resp.content = "VALID: Looks good."
    
    # 3. Polisher response
    polisher_resp = MagicMock()
    polisher_resp.content = "# ADR 0001: Polished\nFinal version."
    
    # 4. Mermaid response (from polisher call)
    mermaid_resp = MagicMock()
    mermaid_resp.content = "NONE"

    mock_llm.ainvoke.side_effect = [
        actor_resp,
        critic_resp,
        polisher_resp,
        mermaid_resp
    ]
    
    initial_state = {
        "project_dna": mock_dna,
        "temporal_context": mock_temporal,
        "max_iterations": 3,
        "iteration": 0,
        "draft_adr": "",
        "critique": "",
        "final_adr": "",
        "is_valid": False
    }
    
    result = await synthesis_engine.ainvoke(initial_state)
    
    assert "final_adr" in result
    assert "Polished" in result["final_adr"]
    assert result["iteration"] == 1


@pytest.mark.asyncio
@patch("chronos_link.diagramming.mermaid.get_llm")
@patch("chronos_link.synthesis.nodes.get_llm")
async def test_graph_looping(mock_get_llm, mock_mermaid_get_llm, mock_dna, mock_temporal) -> None:
    """Test that the graph loops when the Critic returns INVALID."""
    
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock()
    mock_get_llm.return_value = mock_llm
    mock_mermaid_get_llm.return_value = mock_llm
    
    # Responses: Actor -> Critic (INVALID) -> Actor -> Critic (VALID) -> Polisher -> Mermaid
    responses = [
        MagicMock(content="Draft 1"),
        MagicMock(content="INVALID: Fix things."),
        MagicMock(content="Draft 2"),
        MagicMock(content="VALID"),
        MagicMock(content="Polished ADR"),
        MagicMock(content="NONE")
    ]
    mock_llm.ainvoke.side_effect = responses
    
    initial_state = {
        "project_dna": mock_dna,
        "temporal_context": mock_temporal,
        "max_iterations": 3,
        "iteration": 0,
        "draft_adr": "",
        "critique": "",
        "final_adr": "",
        "is_valid": False
    }
    
    result = await synthesis_engine.ainvoke(initial_state)
    
    assert result["iteration"] == 2
    assert "Polished ADR" in result["final_adr"]
