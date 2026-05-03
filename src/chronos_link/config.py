"""Centralized configuration via Pydantic BaseSettings.

Environment variables or a .env file are loaded automatically.
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-wide settings resolved from environment / .env."""

    # --- LLM -----------------------------------------------------------------
    llm_provider: str = "google"  # google, ollama, anthropic
    llm_model: str = "gemini-2.0-flash"
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # --- Workspace -----------------------------------------------------------
    workspace_root: Path = Path(".")

    # --- ADR output ----------------------------------------------------------
    adr_output_dir: str = "docs/adr"

    # --- Temporal layer ------------------------------------------------------
    k_window: int = 5

    # --- Synthesis layer -----------------------------------------------------
    max_iterations: int = 3
    ci_mode: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def adr_dir(self) -> Path:
        """Resolved absolute path to the ADR output directory."""
        return (self.workspace_root / self.adr_output_dir).resolve()


# Singleton – importable anywhere as ``from chronos_link.config import settings``
settings = Settings()
