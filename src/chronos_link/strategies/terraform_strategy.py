"""Strategies Layer — Terraform Strategy.

Specific architectural logic for Terraform/IaC projects.
"""

from __future__ import annotations

import re
from pathlib import Path
from chronos_link.strategies.base import BaseStrategy


class TerraformStrategy(BaseStrategy):
    """Strategy for Terraform projects (detected via *.tf files)."""

    def get_stack_name(self) -> str:
        return "Terraform (Infrastructure as Code)"

    def get_anti_patterns(self) -> list[str]:
        return [
            "Hard-coded values (use variables instead)",
            "Missing provider version constraints",
            "Massive monolithic state files (favor modularization)",
            "Using local state in production",
            "Sensitive data in plaintext variables"
        ]

    def get_consequence_templates(self) -> dict[str, str]:
        return {
            "Module vs Resource": "Modules increase reusability but can hide complexity.",
            "Remote State Locking": "Essential for team collaboration to prevent state corruption."
        }

    def verify_dependency(self, name: str) -> bool:
        """Check for provider or module usage in *.tf files."""
        # Check all .tf files in the root for the name
        for tf_file in self.root.glob("*.tf"):
            try:
                if re.search(fr"\b{re.escape(name)}\b", tf_file.read_text(encoding="utf-8")):
                    return True
            except OSError:
                continue
        return False
