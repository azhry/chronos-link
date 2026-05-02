"""Tests for the Strategies Layer."""

from __future__ import annotations

from pathlib import Path
import pytest
from chronos_link.strategies.go_strategy import GoStrategy
from chronos_link.strategies.terraform_strategy import TerraformStrategy
from chronos_link.strategies.registry import resolve_strategies
from chronos_link.perception.models import ProjectDNA, StackSignature, StackType


def test_go_strategy_anti_patterns(tmp_path) -> None:
    strategy = GoStrategy(tmp_path)
    aps = strategy.get_anti_patterns()
    assert len(aps) > 0
    assert any("init()" in ap for ap in aps)


def test_go_dependency_verification(tmp_path) -> None:
    (tmp_path / "go.mod").write_text("module test\nrequire github.com/gin-gonic/gin v1.9.1", encoding="utf-8")
    strategy = GoStrategy(tmp_path)
    assert strategy.verify_dependency("gin") is True
    assert strategy.verify_dependency("beego") is False


def test_terraform_dependency_verification(tmp_path) -> None:
    (tmp_path / "main.tf").write_text('provider "aws" {}', encoding="utf-8")
    strategy = TerraformStrategy(tmp_path)
    assert strategy.verify_dependency("aws") is True
    assert strategy.verify_dependency("azure") is False


def test_resolve_strategies(tmp_path) -> None:
    dna = ProjectDNA(
        root=tmp_path,
        signatures=[
            StackSignature(manifest_path=tmp_path/"go.mod", stack_type=StackType.GO),
            StackSignature(manifest_path=tmp_path/"main.tf", stack_type=StackType.TERRAFORM)
        ]
    )
    strategies = resolve_strategies(dna)
    assert len(strategies) == 2
    names = {s.get_stack_name() for s in strategies}
    assert "Go (Golang)" in names
    assert "Terraform (Infrastructure as Code)" in names
