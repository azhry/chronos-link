"""CLI entry point for Chronos-Link-V1.

Usage:
    chronos_link generate          Generate an ADR from the current workspace.
    chronos_link generate --help   Show all options.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer

from chronos_link.config import settings

app = typer.Typer(
    name="chronos_link",
    help="Dynamic Agentic Knowledge Engine — autonomous ADR synthesis.",
    add_completion=False,
)


import asyncio
from chronos_link.perception import probe
from chronos_link.temporal import retrieve_context
from chronos_link.synthesis.graph import synthesis_engine
from chronos_link.sequencing.manager import SequenceManager


async def run_chronos_link_pipeline(root: Path, k: int):
    """Orchestrate all phases of the Chronos-Link-V1 pipeline."""
    # 1. Perception Layer
    if not settings.ci_mode:
        typer.echo(f"\n[CHRONOS-LINK] [1/4] Probing environment... (Using {settings.llm_provider.upper()}: {settings.llm_model})")
    dna = probe(root)
    if not settings.ci_mode:
        typer.echo(f"[CHRONOS-LINK] [OK] Detected stacks: {[s.stack_type.value for s in dna.signatures]}")

    # 2. Temporal Layer
    if not settings.ci_mode:
        typer.echo("[CHRONOS-LINK] [2/4] Retrieving temporal context...")
    context = retrieve_context(root, settings.adr_dir, k)
    if not settings.ci_mode:
        typer.echo(f"[CHRONOS-LINK] [OK] Context retrieved (History: {len(context.historical_adrs)} ADRs)")

    # 3. Sequencing Layer
    if not settings.ci_mode:
        typer.echo("[CHRONOS-LINK] [3/4] Preparing ADR sequence...")
    seq = SequenceManager(settings.adr_dir)
    if not settings.adr_dir.exists():
        settings.adr_dir.mkdir(parents=True)
    
    if not seq.acquire_lock():
        typer.echo("[CHRONOS-LINK] [ERROR] Could not acquire ADR lock. Concurrent generation detected?")
        raise typer.Exit(code=1)
    
    try:
        next_id = seq.next_id()
        if not settings.ci_mode:
            typer.echo(f"[CHRONOS-LINK] [OK] Next ADR ID: {next_id}")

        # 4. Synthesis Layer
        if not settings.ci_mode:
            typer.echo("[CHRONOS-LINK] [4/4] Synthesizing ADR (Actor-Critic loop)...")
        
        initial_state = {
            "project_dna": dna,
            "temporal_context": context,
            "max_iterations": settings.max_iterations,
            "iteration": 0,
            "draft_adr": "",
            "critique": "",
            "final_adr": "",
            "is_valid": False
        }
        
        result = await synthesis_engine.ainvoke(initial_state)
        final_content = result["final_adr"]
        
        # Save the result
        filename = f"{next_id}-architectural-decision.md"
        output_path = settings.adr_dir / filename
        output_path.write_text(final_content, encoding="utf-8")
        
        if settings.ci_mode:
            # Output ONLY the final content to stdout for CI/CD to capture
            typer.echo(final_content)
        else:
            typer.echo(f"[CHRONOS-LINK] [SUCCESS] ADR saved to: {output_path}")
        
    finally:
        seq.release_lock()


@app.command()
def generate(
    workspace: Annotated[
        Optional[Path],
        typer.Option("--workspace", "-w", help="Workspace root to analyse."),
    ] = None,
    k: Annotated[
        int,
        typer.Option("--k", help="Number of historical ADRs to consider (K-window)."),
    ] = settings.k_window,
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help="LLM provider (google, ollama, anthropic, openrouter)."),
    ] = settings.llm_provider,
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="LLM model name."),
    ] = settings.llm_model,
    ci: Annotated[
        bool,
        typer.Option("--ci", help="CI mode: suppress logs, output final ADR to stdout."),
    ] = False,
) -> None:
    """Generate an Architecture Decision Record for the current workspace."""
    if workspace:
        settings.workspace_root = workspace.resolve()
    
    settings.llm_provider = provider
    settings.llm_model = model
    settings.ci_mode = ci
        
    root = settings.workspace_root
    
    # Run the async pipeline
    asyncio.run(run_chronos_link_pipeline(root, k))



if __name__ == "__main__":
    app()
