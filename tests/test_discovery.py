"""Tests for the Perception Layer — DiscoveryEngine, Constitution, and probe()."""

from __future__ import annotations

from pathlib import Path

from chronos_link.perception import probe
from chronos_link.perception.constitution import load_constitution
from chronos_link.perception.discovery import DiscoveryEngine
from chronos_link.perception.models import StackType


# ── DiscoveryEngine tests ──────────────────────────────────────────────────


class TestDiscoveryEngine:
    """Unit tests for DiscoveryEngine.scan()."""

    def test_empty_directory(self, tmp_workspace: Path) -> None:
        """Empty workspace returns no signatures."""
        engine = DiscoveryEngine(tmp_workspace)
        assert engine.scan() == []

    def test_go_project(self, go_workspace: Path) -> None:
        """Detects go.mod and Dockerfile in a simple Go project."""
        sigs = DiscoveryEngine(go_workspace).scan()
        types = {s.stack_type for s in sigs}
        assert StackType.GO in types
        assert StackType.DOCKER in types

    def test_go_context_extraction(self, go_workspace: Path) -> None:
        """Extracts Go module name from go.mod."""
        sigs = DiscoveryEngine(go_workspace).scan()
        go_sig = next(s for s in sigs if s.stack_type == StackType.GO)
        assert go_sig.context == "github.com/example/myservice"

    def test_monorepo_detects_all_stacks(self, monorepo_workspace: Path) -> None:
        """Monorepo with Go, Node, Terraform, and Helm detects all four."""
        sigs = DiscoveryEngine(monorepo_workspace).scan()
        types = {s.stack_type for s in sigs}
        assert StackType.GO in types
        assert StackType.NODE in types
        assert StackType.TERRAFORM in types
        assert StackType.HELM in types

    def test_node_context_extraction(self, monorepo_workspace: Path) -> None:
        """Extracts package name from package.json."""
        sigs = DiscoveryEngine(monorepo_workspace).scan()
        node_sig = next(s for s in sigs if s.stack_type == StackType.NODE)
        assert node_sig.context == "mono-web"

    def test_max_depth_limits_scan(self, monorepo_workspace: Path) -> None:
        """max_depth=0 only scans root — misses nested manifests."""
        sigs = DiscoveryEngine(monorepo_workspace, max_depth=0).scan()
        # Only the charts/ directory is at depth 1 from root,
        # but Go/Node/TF are at depth 2+ — depth=0 finds only root-level items.
        types = {s.stack_type for s in sigs}
        # None of the manifests are at the root of monorepo_workspace
        assert StackType.GO not in types

    def test_skips_node_modules(self, tmp_workspace: Path) -> None:
        """node_modules directory is not descended into."""
        nm = tmp_workspace / "node_modules" / "some-pkg"
        nm.mkdir(parents=True)
        (nm / "package.json").write_text('{"name":"internal"}', encoding="utf-8")
        sigs = DiscoveryEngine(tmp_workspace).scan()
        assert all(s.stack_type != StackType.NODE for s in sigs)

    def test_csproj_detection(self, tmp_workspace: Path) -> None:
        """Detects .NET projects via *.csproj regex."""
        (tmp_workspace / "MyApp.csproj").write_text(
            "<Project></Project>", encoding="utf-8"
        )
        sigs = DiscoveryEngine(tmp_workspace).scan()
        assert any(s.stack_type == StackType.DOTNET for s in sigs)

    def test_docker_compose_yml(self, tmp_workspace: Path) -> None:
        """Detects docker-compose.yml (not just .yaml)."""
        (tmp_workspace / "docker-compose.yml").write_text(
            "version: '3'\nservices: {}", encoding="utf-8"
        )
        sigs = DiscoveryEngine(tmp_workspace).scan()
        assert any(s.stack_type == StackType.DOCKER_COMPOSE for s in sigs)

    def test_no_duplicates(self, go_workspace: Path) -> None:
        """Each manifest path appears at most once."""
        sigs = DiscoveryEngine(go_workspace).scan()
        paths = [s.manifest_path for s in sigs]
        assert len(paths) == len(set(paths))


# ── Constitution loader tests ──────────────────────────────────────────────


class TestConstitutionLoader:
    """Tests for load_constitution()."""

    def test_loads_adr_rules(self, constitution_workspace: Path) -> None:
        """Reads .adr-rules when present."""
        text = load_constitution(constitution_workspace)
        assert text is not None
        assert "Hexagonal Architecture" in text

    def test_returns_none_when_absent(self, tmp_workspace: Path) -> None:
        """Returns None when no constitution file exists."""
        assert load_constitution(tmp_workspace) is None

    def test_prefers_adr_rules_over_prompt_md(self, tmp_workspace: Path) -> None:
        """When both files exist, .adr-rules takes precedence."""
        (tmp_workspace / ".adr-rules").write_text("RULE A", encoding="utf-8")
        (tmp_workspace / "PROMPT.md").write_text("RULE B", encoding="utf-8")
        text = load_constitution(tmp_workspace)
        assert text == "RULE A"

    def test_falls_back_to_prompt_md(self, tmp_workspace: Path) -> None:
        """Uses PROMPT.md when .adr-rules is absent."""
        (tmp_workspace / "PROMPT.md").write_text("Fallback rules", encoding="utf-8")
        text = load_constitution(tmp_workspace)
        assert text == "Fallback rules"


# ── Integration: probe() ───────────────────────────────────────────────────


class TestProbe:
    """Integration tests for the top-level probe() function."""

    def test_go_docker_workspace(self, go_workspace: Path) -> None:
        """probe() aggregates stack signatures and constitution."""
        dna = probe(go_workspace)
        types = {s.stack_type for s in dna.signatures}
        assert StackType.GO in types
        assert StackType.DOCKER in types
        assert dna.constitution is None

    def test_monorepo_returns_all_stacks(self, monorepo_workspace: Path) -> None:
        """probe() on a monorepo returns all nested stacks."""
        dna = probe(monorepo_workspace)
        types = {s.stack_type for s in dna.signatures}
        assert len(types) >= 4  # Go, Node, Terraform, Helm

    def test_constitution_included(self, constitution_workspace: Path) -> None:
        """probe() includes the constitution text when available."""
        dna = probe(constitution_workspace)
        assert dna.constitution is not None
        assert "gRPC" in dna.constitution

    def test_root_resolved(self, tmp_workspace: Path) -> None:
        """probe() resolves the root to an absolute path."""
        dna = probe(tmp_workspace)
        assert dna.root.is_absolute()
