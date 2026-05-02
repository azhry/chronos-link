"""Strategies Layer — NLP Strategy.

Specific architectural logic for Machine Learning and NLP projects.
"""

from __future__ import annotations

import re
from pathlib import Path
from chronos_link.strategies.base import BaseStrategy


class NLPStrategy(BaseStrategy):
    """Strategy for NLP/ML projects (detected via requirements.txt/pyproject.toml)."""

    def get_stack_name(self) -> str:
        return "NLP / Machine Learning"

    def get_anti_patterns(self) -> list[str]:
        return [
            "Unbounded batch sizes causing OOM (Out of Memory)",
            "Missing GPU/CPU fallback logic",
            "Lack of model versioning (relying on 'latest')",
            "Synchronous inference in latency-critical paths",
            "Hard-coded model paths"
        ]

    def get_consequence_templates(self) -> dict[str, str]:
        return {
            "Quantization": "Reduces model size and latency but may slightly decrease accuracy.",
            "Batching": "Increases throughput but can increase individual request latency."
        }

    def verify_dependency(self, name: str) -> bool:
        """Check for library usage in common Python manifests."""
        for manifest in ["requirements.txt", "pyproject.toml"]:
            path = self.root / manifest
            if path.is_file():
                try:
                    if re.search(fr"\b{re.escape(name)}\b", path.read_text(encoding="utf-8")):
                        return True
                except OSError:
                    continue
        return False
