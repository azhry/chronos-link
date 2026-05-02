"""Synthesis Layer — Node implementations.

Individual functions for Actor, Critic, and Polisher nodes.
"""

from __future__ import annotations

import json
from google import genai
from google.genai import types
from chronos_link.config import settings
from chronos_link.synthesis.state import AgentState
from chronos_link.synthesis import prompts


from langchain_core.messages import HumanMessage, SystemMessage
from chronos_link.synthesis.llm import get_llm
from chronos_link.strategies.registry import resolve_strategies
from chronos_link.diagramming.mermaid import generate_mermaid


async def actor_node(state: AgentState) -> dict:
    """Drafts the initial ADR or refines it based on critique."""
    it = state.get("iteration", 0) + 1
    if not settings.ci_mode:
        print(f"  [ACTOR] Generating draft (Iteration {it})...")
    llm = get_llm()
    
    dna_str = state["project_dna"].model_dump_json(indent=2)
    temporal_str = state["temporal_context"].model_dump_json(indent=2)
    
    # Get strategy hints
    strategies = resolve_strategies(state["project_dna"])
    strategy_hints = "\n".join(s.get_strategy_hints() for s in strategies)
    
    user_msg = prompts.ACTOR_USER_PROMPT.format(
        dna=dna_str,
        temporal=temporal_str,
        strategy_hints=strategy_hints,
        critique=state.get("critique", "None"),
        previous_draft=state.get("draft_adr", "None")
    )
    
    messages = [
        SystemMessage(content=prompts.ACTOR_SYSTEM_PROMPT),
        HumanMessage(content=user_msg)
    ]
    
    response = await llm.ainvoke(messages)
    
    return {
        "draft_adr": response.content,
        "iteration": 1
    }


async def critic_node(state: AgentState) -> dict:
    """Critiques the ADR draft against constraints and history."""
    if not settings.ci_mode:
        print("  [CRITIC] Reviewing draft...")
    llm = get_llm()
    
    dna_str = state["project_dna"].model_dump_json(indent=2)
    temporal_str = state["temporal_context"].model_dump_json(indent=2)
    
    # Get strategy hints
    strategies = resolve_strategies(state["project_dna"])
    strategy_hints = "\n".join(s.get_strategy_hints() for s in strategies)
    
    user_msg = prompts.CRITIC_USER_PROMPT.format(
        dna=dna_str,
        temporal=temporal_str,
        draft=state["draft_adr"],
        strategy_hints=strategy_hints
    )
    
    messages = [
        SystemMessage(content=prompts.CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=user_msg)
    ]
    
    response = await llm.ainvoke(messages)
    
    text = str(response.content).strip()
    is_valid = text.upper().startswith("VALID")
    
    if is_valid:
        if not settings.ci_mode:
            print("  [CRITIC] Draft approved.")
    else:
        if not settings.ci_mode:
            print(f"  [CRITIC] Draft rejected. Feedback: {text[:100]}...")

    return {
        "is_valid": is_valid,
        "critique": text if not is_valid else ""
    }


async def polisher_node(state: AgentState) -> dict:
    """Polishes the validated draft and applies the template."""
    if not settings.ci_mode:
        print("  [POLISHER] Finalizing ADR format and diagrams...")
    llm = get_llm()
    
    user_msg = prompts.POLISHER_USER_PROMPT.format(
        draft=state["draft_adr"]
    )
    
    messages = [
        SystemMessage(content=prompts.POLISHER_SYSTEM_PROMPT),
        HumanMessage(content=user_msg)
    ]
    
    response = await llm.ainvoke(messages)
    
    polished_content = str(response.content)
    
    # 1. Generate Mermaid diagram if applicable
    diagram = await generate_mermaid(polished_content, state["project_dna"])
    
    return {
        "final_adr": polished_content,
        "diagram": diagram
    }
