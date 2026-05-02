"""Synthesis Layer — Graph Assembly.

Defines the LangGraph state machine structure and conditional routing.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import StateGraph, END

from chronos_link.synthesis.state import AgentState
from chronos_link.synthesis.nodes import actor_node, critic_node, polisher_node


def should_continue(state: AgentState) -> Literal["polisher", "actor"]:
    """Determines whether to loop back to the Actor or proceed to the Polisher."""
    if state["is_valid"] or state["iteration"] >= state["max_iterations"]:
        return "polisher"
    return "actor"


def create_synthesis_graph() -> StateGraph:
    """Assemble the reflexive state machine graph."""
    workflow = StateGraph(AgentState)

    # 1. Add nodes
    workflow.add_node("actor", actor_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("polisher", polisher_node)

    # 2. Define edges
    workflow.set_entry_point("actor")
    workflow.add_edge("actor", "critic")
    
    # Conditional edge from Critic
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "polisher": "polisher",
            "actor": "actor"
        }
    )
    
    workflow.add_edge("polisher", END)

    return workflow


# Compiled graph instance
synthesis_engine = create_synthesis_graph().compile()
