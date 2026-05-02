"""Diagramming Layer — Mermaid.js Generator.

Uses an LLM to determine if an architectural decision involves service
boundaries and generates a Mermaid.js diagram if so.
"""

from __future__ import annotations

from google import genai
from google.genai import types
from chronos_link.config import settings
from chronos_link.perception.models import ProjectDNA


_MERMAID_PROMPT = """You are a technical architect specializing in Mermaid.js diagrams.
Analyze the following architectural decision.

If the decision involves service boundaries, data flow between components, or changes in infrastructure topology:
1. Generate a Mermaid.js 'graph TD' or 'sequenceDiagram' snippet.
2. Ensure the diagram is clear and uses professional terminology.

If the decision does NOT involve architectural topology (e.g., just changing a library version or a local code refactor):
1. Respond ONLY with the word 'NONE'.

DECISION:
{decision}

PROJECT DNA:
{dna}

Output ONLY the Mermaid code block (without backticks) or 'NONE'.
"""


from chronos_link.synthesis.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


async def generate_mermaid(decision_text: str, dna: ProjectDNA) -> str | None:
    """Generate a Mermaid diagram for a decision if applicable."""
    llm = get_llm()
    
    dna_str = dna.model_dump_json(indent=2)
    
    messages = [
        SystemMessage(content="Generate Mermaid.js diagrams for architectural changes."),
        HumanMessage(content=_MERMAID_PROMPT.format(decision=decision_text, dna=dna_str))
    ]
    
    response = await llm.ainvoke(messages)
    
    text = str(response.content).strip()
    if text.upper() == "NONE":
        return None
        
    # Clean up backticks if the LLM included them
    text = text.replace("```mermaid", "").replace("```", "").strip()
    return text
