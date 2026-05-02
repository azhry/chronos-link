"""Strategies Layer — Go Strategy.

Specific architectural logic for Go (Golang) projects.
"""

from __future__ import annotations

import re
from pathlib import Path
from chronos_link.strategies.base import BaseStrategy


class GoStrategy(BaseStrategy):
    """Strategy for Go projects (detected via go.mod)."""

    def get_stack_name(self) -> str:
        return "Go (Golang)"

    def get_anti_patterns(self) -> list[str]:
        return [
            "Shared global state (e.g., global variables for DB pools)",
            "Abuse of init() functions for logic",
            "Fat interfaces (interfaces should be small, often 1-2 methods)",
            "Ignoring errors or using '_' to suppress them",
            "Goroutine leaks (unbounded goroutine creation)"
        ]

    def get_consequence_templates(self) -> dict[str, str]:
        return {
            "gRPC vs REST": "gRPC offers better performance and type safety but higher complexity.",
            "Channels vs Mutex": "Channels for communication; Mutexes for state protection.",
            "Standard Library vs Frameworks": "Prefer stdlib for longevity and minimal dependencies."
        }

    def verify_dependency(self, name: str) -> bool:
        """Check if a dependency exists in go.mod."""
        go_mod = self.root / "go.mod"
        if not go_mod.is_file():
            return False
            
        try:
            content = go_mod.read_text(encoding="utf-8")
            # Simple regex to check for the dependency name in go.mod
            return bool(re.search(fr"\b{re.escape(name)}\b", content))
        except OSError:
            return False
