"""Tests for the GitWrapper."""

from __future__ import annotations

import os
from pathlib import Path
from git import Repo
import pytest

from chronos_link.temporal.git_wrapper import GitWrapper


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository with some history."""
    repo = Repo.init(tmp_path)
    
    # Create an initial commit
    file1 = tmp_path / "README.md"
    file1.write_text("Initial content", encoding="utf-8")
    repo.index.add([str(file1)])
    repo.index.commit("Initial commit")
    
    return tmp_path


def test_git_wrapper_init(git_repo: Path) -> None:
    """GitWrapper initializes correctly in a git repo."""
    wrapper = GitWrapper(git_repo)
    assert wrapper.repo is not None


def test_git_wrapper_no_repo(tmp_path: Path) -> None:
    """GitWrapper fails to initialize outside a git repo."""
    from git import InvalidGitRepositoryError
    with pytest.raises(InvalidGitRepositoryError):
        GitWrapper(tmp_path)


def test_get_staged_diff(git_repo: Path) -> None:
    """GitWrapper correctly identifies staged changes."""
    wrapper = GitWrapper(git_repo)
    
    # Create and stage a change
    file1 = git_repo / "README.md"
    file1.write_text("Modified content", encoding="utf-8")
    repo = Repo(git_repo)
    repo.index.add([str(file1)])
    
    diff = wrapper.get_staged_diff()
    assert "Modified content" in diff


def test_get_last_commit_diff(git_repo: Path) -> None:
    """GitWrapper retrieves the last commit diff."""
    wrapper = GitWrapper(git_repo)
    
    # Create another commit
    file2 = git_repo / "test.txt"
    file2.write_text("Hello", encoding="utf-8")
    repo = Repo(git_repo)
    repo.index.add([str(file2)])
    repo.index.commit("Add test.txt")
    
    diff = wrapper.get_last_commit_diff()
    assert "Add test.txt" in diff
    assert "Hello" in diff


def test_extract_signals() -> None:
    """Architecture signal extraction works as expected."""
    message = "Refactor the authentication module; Migrate to PostgreSQL"
    signals = GitWrapper.extract_signals(message)
    
    keywords = {s.keyword.lower() for s in signals}
    assert "refactor" in keywords
    assert "migrate" in keywords
    assert len(signals) == 2


def test_build_delta(git_repo: Path) -> None:
    """build_delta constructs a complete ArchitecturalDelta."""
    wrapper = GitWrapper(git_repo)
    
    # Create a previous commit with signals
    file2 = git_repo / "signal.txt"
    file2.write_text("signal", encoding="utf-8")
    wrapper.repo.index.add([str(file2)])
    wrapper.repo.index.commit("Refactor: add signal.txt")

    # Modify and stage a NEW change AFTER the commit
    file1 = git_repo / "README.md"
    file1.write_text("Staged change", encoding="utf-8")
    wrapper.repo.index.add([str(file1)])
    
    delta = wrapper.build_delta()
    assert "Staged change" in delta.staged_diff
    assert "Refactor: add signal.txt" in delta.last_commit_message
    assert any(s.keyword.lower() == "refactor" for s in delta.signals)
