"""Strategies Layer — Registry.

Maps StackTypes to concrete strategy implementations.
"""

from __future__ import annotations

from pathlib import Path
from chronos_link.perception.models import ProjectDNA, StackType
from chronos_link.strategies.base import BaseStrategy
from chronos_link.strategies.go_strategy import GoStrategy
from chronos_link.strategies.terraform_strategy import TerraformStrategy
from chronos_link.strategies.nlp_strategy import NLPStrategy


class DefaultStrategy(BaseStrategy):
    """Fallback strategy for unknown stacks."""
    def get_stack_name(self) -> str: return "Generic"
    def get_anti_patterns(self) -> list[str]: return []
    def get_consequence_templates(self) -> dict[str, str]: return {}
    def verify_dependency(self, name: str) -> bool: return False


_STRATEGY_MAP = {
    StackType.GO: GoStrategy,
    StackType.TERRAFORM: TerraformStrategy,
    StackType.PYTHON: NLPStrategy,  # Simple mapping for now
}


def resolve_strategies(dna: ProjectDNA) -> list[BaseStrategy]:
    """Resolve all applicable strategies based on detected stack signatures."""
    strategies: list[BaseStrategy] = []
    seen_types = {s.stack_type for s in dna.signatures}
    
    for stack_type in seen_types:
        strategy_cls = _STRATEGY_MAP.get(stack_type)
        if strategy_cls:
            strategies.append(strategy_cls(dna.root))
            
    if not strategies:
        strategies.append(DefaultStrategy(dna.root))
        
    return strategies
