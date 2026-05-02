"""Strategies Layer — Base Class.

Defines the interface for pluggable technology-specific architectural logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseStrategy(ABC):
    """Abstract base class for all stack-specific strategies.

    Strategies provide domain knowledge (anti-patterns, templates) that
    the Critic node uses to validate ADRs.
    """

    def __init__(self, workspace_root: Path) -> None:
        self.root = workspace_root

    @abstractmethod
    def get_stack_name(self) -> str:
        """Return the human-readable name of the stack."""
        pass

    @abstractmethod
    def get_anti_patterns(self) -> list[str]:
        """Return a list of common anti-patterns for this stack."""
        pass

    @abstractmethod
    def get_consequence_templates(self) -> dict[str, str]:
        """Return pre-populated trade-off lists for this stack."""
        pass

    @abstractmethod
    def verify_dependency(self, name: str) -> bool:
        """Check if a specific dependency/library exists in the project."""
        pass

    def get_strategy_hints(self) -> str:
        """Format strategy knowledge into a string for the LLM prompt."""
        anti_patterns = "\n".join(f"- {ap}" for ap in self.get_anti_patterns())
        templates = "\n".join(f"- {k}: {v}" for k, v in self.get_consequence_templates().items())
        
        return f"""
STACK: {self.get_stack_name()}
COMMON ANTI-PATTERNS:
{anti_patterns}

TYPICAL CONSEQUENCES/TRADE-OFFS:
{templates}
"""
