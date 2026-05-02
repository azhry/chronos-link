"""Tests for the Sequencing Layer."""

from __future__ import annotations

from pathlib import Path
import pytest
from chronos_link.sequencing.manager import SequenceManager


def test_next_id_empty(tmp_path) -> None:
    manager = SequenceManager(tmp_path)
    assert manager.next_id() == "0001"


def test_next_id_existing(sample_adr_dir) -> None:
    manager = SequenceManager(sample_adr_dir)
    assert manager.next_id() == "0008"


def test_check_integrity_gaps(tmp_path) -> None:
    (tmp_path / "0001-test.md").touch()
    (tmp_path / "0003-test.md").touch()
    
    manager = SequenceManager(tmp_path)
    gaps = manager.check_integrity()
    assert gaps == [2]


def test_locking(tmp_path) -> None:
    manager = SequenceManager(tmp_path)
    
    # 1. Acquire lock
    assert manager.acquire_lock() is True
    assert manager.lock_file.exists()
    
    # 2. Try to acquire again (should fail or timeout)
    assert manager.acquire_lock(timeout=1) is False
    
    # 3. Release lock
    manager.release_lock()
    assert not manager.lock_file.exists()
    
    # 4. Acquire again (should succeed now)
    assert manager.acquire_lock() is True
    manager.release_lock()
