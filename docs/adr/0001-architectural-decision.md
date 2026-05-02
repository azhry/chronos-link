# ADR 0001: Adopt Initial Commit Environment Variable Configuration Schema

## Status
Accepted

## Context
The Chronos-Link project’s first commit (hash `2118534b66f1f4db77ef13ef6315975c03bebd66`) introduces the baseline project structure, including `.env.example`, `.gitignore`, and `README.md`, as confirmed by the provided Git delta. The detected `pyproject.toml` manifest confirms a Python-based NLP/ML stack, with mandatory alignment to the Chronos-Link Architectural Constitution:
- **Article 1 (Provider Agnosticism)**: All LLM interactions must use LangChain abstractions; orchestration logic must not couple to proprietary provider SDKs. Enforcement is code-level via LangChain integrations, not configuration restrictions.
- **Article 2 (Evidence-Based Synthesis)**: All decisions must derive from verifiable project signals (committed file content, Git history). This decision is derived exclusively from the file structure in the initial commit, as the Temporal/Perception layer signals array is empty in the provided delta.
- **Article 3 (Stateless & Deterministic Orchestration)**: Core agent workflow must be defined as a LangGraph directed graph, with state explicitly passed via the `AgentState` object. Nodes may only interact with `AgentState`, with no hidden state permitted between nodes.
- **Article 4 (Async-First I/O)**: All external I/O (LLM calls, filesystem probes, network requests) must use non-blocking `asyncio`/`await` implementations. Compliance is enforced in code, not via environment variables.
- **Article 5 (Zero-Friction Perception)**: Project setup must be zero-config by default; the `probe()` engine must auto-detect common stacks (including Python, per the manifest).
- **Article 6 (Markdown-Standard Output)**: Generated ADRs must follow MADR-compliant markdown, stored in a version-control-friendly path.

Common Python NLP/ML anti-patterns (synchronous inference, unversioned model references, hardcoded runtime parameters) guide the configuration design. The initial `.env.example` defines only the following verifiable configuration keys, with no additional parameters present in the commit: `LLM_PROVIDER`, `LLM_MODEL`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OLLAMA_BASE_URL`, `K_WINDOW`, `MAX_ITERATIONS`, `WORKSPACE_ROOT`, `ADR_OUTPUT_DIR`.

## Decision
Adopt the environment-variable-driven configuration schema defined in the initial commit’s `.env.example`, with strict alignment to all Architectural Constitution articles:

1. **Provider Agnosticism (Article 1 Compliance)**
   - `LLM_PROVIDER` accepts only three validated values: `google`, `anthropic`, `ollama`, which map exclusively to official LangChain integrations (LangChain Google Generative AI, LangChain Anthropic, LangChain Ollama) in implementation code. No orchestration logic uses proprietary provider SDKs directly, as enforced via LangChain abstractions per Article 1.
   - Provider-specific credential fields are gated by the selected `LLM_PROVIDER` value: `GEMINI_API_KEY` (mandatory for `google`), `ANTHROPIC_API_KEY` (mandatory for `anthropic`), `OLLAMA_BASE_URL` (mandatory for `ollama`, default `http://localhost:11434` per the committed `.env.example`).
   - No configuration-level prohibitions on SDK parameters are imposed; provider agnosticism is enforced entirely via LangChain integration code, not config rules.

2. **Model Versioning (NLP/ML Best Practice)**
   - Mandate explicit `LLM_MODEL` field (default: `gemini-2.0-flash`) to eliminate reliance on mutable `latest` model tags, preventing regressions from unversioned model updates.

3. **Runtime Parameter Configuration (No Hardcoded Values)**
   - All user-overridable runtime parameters are sourced exclusively from the committed `.env.example`:
     - `K_WINDOW=5`: Default count of past ADRs retrieved for context synthesis.
     - `MAX_ITERATIONS=3`: Default maximum Actor-Critic loop iterations.
     - `WORKSPACE_ROOT=.`: Default root path for project analysis.
     - `ADR_OUTPUT_DIR=docs/adr`: Default output path for MADR-compliant markdown ADRs, aligning with Article 6.

4. **Stateless Orchestration Alignment (Article 3 Compliance)**
   - Explicitly inject all configuration values into the LangGraph `AgentState` object; no hidden state is permitted outside the directed graph workflow. All nodes access provider, model, and runtime settings exclusively via `AgentState`, ensuring full auditability of the orchestration loop.

5. **Async-First I/O Alignment (Article 4 Compliance)**
   - No environment variables govern async behavior; Article 4 compliance is enforced via `asyncio`/`await` implementations for all I/O-bound operations (LLM calls, filesystem probes, network requests) in code, not configuration.

6. **Zero-Friction Onboarding (Article 5 Compliance)**
   - `.env.example` provides defaults for all optional parameters; users only populate credential fields required for their selected `LLM_PROVIDER`. `.gitignore` excludes `.env` from version control to prevent credential leakage. `.env.example` is the sole canonical configuration template to support zero-config setup.

## Consequences

### Positive
- **Evidence-Based Alignment**: Decision derived exclusively from verifiable committed file content (`.env.example`, `.gitignore`) per Article 2, with no unsubstantiated parameters.
- **Provider Agnosticism**: LangChain-only integration requirements prevent orchestration coupling to proprietary provider SDKs, complying with Article 1.
- **Stateless Orchestration**: Explicit passing of all configuration values via LangGraph `AgentState` eliminates hidden state, aligning with Article 3.
- **Async Compliance**: Code-level `asyncio` enforcement eliminates synchronous inference anti-patterns common in Python NLP/ML stacks, per Article 4.
- **Zero-Friction Setup**: Default values for all parameters minimize setup overhead; only provider-specific credentials require manual entry, complying with Article 5.
- **Model Versioning**: Explicit `LLM_MODEL` values prevent regressions from unversioned model updates, addressing a common Python NLP/ML anti-pattern.
- **Credential Security**: Exclusion of `.env` from version control prevents accidental exposure of API keys and local model endpoints.
- **MADR Compliance**: Default `ADR_OUTPUT_DIR` ensures generated ADRs are stored in a version-control-friendly path per Article 6.
- **No Hardcoded Parameters**: All runtime variables are user-overridable via `.env`, eliminating the need for code changes to adjust to project size or workload.

### Negative/Trade-offs
- **Manual Credential Management**: Users must manually populate provider-specific credentials; no automatic credential discovery is implemented, a minor trade-off against zero-friction goals for edge cases.
- **No Dynamic Parameter Tuning**: `K_WINDOW` and `MAX_ITERATIONS` require manual overrides for large-scale monorepo analysis, as no dynamic auto-tuning is implemented.
- **Python Stack Specificity**: Current schema is tailored to the Python NLP/ML stack; separate configuration paths will be required for future non-Python stack support.
- **Validation Overhead**: Runtime `LLM_PROVIDER` validity checks add minor compute overhead, required to enforce provider agnosticism.