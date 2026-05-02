# 📜 Chronos-Link Architectural Constitution

This document defines the core engineering principles and non-negotiable rules for the Chronos-Link engine. All future Architectural Decision Records (ADRs) must align with these articles.

---

## Article 1: Provider Agnosticism
**Rule**: The engine must never be coupled to a specific LLM provider's proprietary SDK for orchestration logic.
**Rationale**: Users must have the freedom to switch between cloud models (Google, Anthropic) and local models (Ollama) to manage cost, latency, and privacy.
**Enforcement**: Use LangChain abstractions for all model interactions.

## Article 2: Evidence-Based Synthesis
**Rule**: Architectural decisions must be derived from verifiable "Signals" in the project (Git history, file structure, dependencies).
**Rationale**: We aim to automate documentation of *real* decisions, not hallucinate hypothetical ones.
**Enforcement**: The Temporal and Perception layers must provide the primary data for the Synthesis loop.

## Article 3: Stateless & Deterministic Orchestration
**Rule**: The core agent workflow must be defined as a directed graph (LangGraph) where state is explicitly passed between nodes.
**Rationale**: Avoids "Hidden State" bugs and allows for clear auditing of how the Actor-Critic loop arrived at a decision.
**Enforcement**: Nodes must only interact with the `AgentState` object.

## Article 4: Async-First I/O
**Rule**: All external interactions (LLM calls, filesystem probes, network requests) must be non-blocking.
**Rationale**: To maintain responsiveness when analyzing large-scale monorepos or multiple projects concurrently.
**Enforcement**: Use `asyncio` and `await` for all I/O-bound operations.

## Article 5: Zero-Friction Perception
**Rule**: Project discovery should be automatic and "zero-config" whenever possible.
**Rationale**: Developers are more likely to use a tool if it "just works" upon installation without requiring complex schema definitions.
**Enforcement**: The `probe()` engine must handle common stack detection (Go, Node, Python, Docker) out of the box.

## Article 6: Markdown-Standard Output
**Rule**: Generated records must follow a human-readable, version-control-friendly markdown format (MADR).
**Rationale**: Documentation must be as accessible to humans as it is to machines.
**Enforcement**: The Polisher node must strictly enforce markdown structure and syntax.
