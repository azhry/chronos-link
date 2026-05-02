"""Tests for the ADRReader."""

from __future__ import annotations

from pathlib import Path
import pytest

from chronos_link.temporal.adr_reader import ADRReader


def test_adr_reader_empty_dir(tmp_path: Path) -> None:
    """ADRReader returns empty list if directory is empty."""
    reader = ADRReader(tmp_path)
    assert reader.read_all() == []


def test_adr_reader_parsing(sample_adr_dir: Path) -> None:
    """ADRReader correctly parses ADR sections."""
    reader = ADRReader(sample_adr_dir)
    entries = reader.read_all()
    
    assert len(entries) == 7
    # Check first entry
    first = entries[0]
    assert first.id == "0001"
    assert "Decision 1" in first.title
    assert "Accepted" in first.status
    assert "thing 1" in first.decision


def test_read_last_k(sample_adr_dir: Path) -> None:
    """read_last_k retrieves exactly K most recent ADRs."""
    reader = ADRReader(sample_adr_dir)
    
    # K = 3
    last_3 = reader.read_last_k(3)
    assert len(last_3) == 3
    assert last_3[0].id == "0005"
    assert last_3[1].id == "0006"
    assert last_3[2].id == "0007"
    
    # K = 10 (more than available)
    last_all = reader.read_last_k(10)
    assert len(last_all) == 7


def test_adr_reader_skips_non_adr_files(tmp_path: Path) -> None:
    """Files not following NNNN-prefix pattern are skipped."""
    (tmp_path / "not-an-adr.md").write_text("# Not an ADR", encoding="utf-8")
    (tmp_path / "0001-valid.md").write_text("# ADR 1: Valid", encoding="utf-8")
    
    reader = ADRReader(tmp_path)
    entries = reader.read_all()
    assert len(entries) == 1
    assert entries[0].id == "0001"
