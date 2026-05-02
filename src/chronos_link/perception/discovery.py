"""DiscoveryEngine — recursive workspace manifest scanner.

Walks the file tree starting from the workspace root and matches known
manifest file names / directory patterns to build a list of
:class:`~chronos_link.perception.models.StackSignature` entries.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from chronos_link.perception.models import StackSignature, StackType

# ---------------------------------------------------------------------------
# Manifest matching rules
# ---------------------------------------------------------------------------
# Each entry: (filename_or_pattern, StackType, is_regex, is_directory)

_FILE_RULES: list[tuple[str, StackType, bool]] = [
    # Backend
    ("go.mod", StackType.GO, False),
    ("package.json", StackType.NODE, False),
    ("requirements.txt", StackType.PYTHON, False),
    ("pyproject.toml", StackType.PYTHON, False),
    ("setup.py", StackType.PYTHON, False),
    # .NET — regex for *.csproj
    (r".*\.csproj$", StackType.DOTNET, True),
    # Cloud Native
    ("Dockerfile", StackType.DOCKER, False),
    ("docker-compose.yaml", StackType.DOCKER_COMPOSE, False),
    ("docker-compose.yml", StackType.DOCKER_COMPOSE, False),
    # Terraform — regex for *.tf
    (r".*\.tf$", StackType.TERRAFORM, True),
]

_DIR_RULES: list[tuple[str, StackType]] = [
    ("charts", StackType.HELM),
    ("k8s", StackType.KUBERNETES),
    ("cluster-api", StackType.CAPI),
]

# Directories that should always be skipped.
_SKIP_DIRS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    "dist",
    "build",
    ".terraform",
}


def _extract_context(manifest_path: Path, stack_type: StackType) -> str:
    """Best-effort extraction of human-readable context from a manifest."""
    try:
        text = manifest_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    if stack_type == StackType.GO:
        # First line of go.mod is typically: module github.com/org/repo
        match = re.search(r"^module\s+(\S+)", text, re.MULTILINE)
        return match.group(1) if match else ""

    if stack_type == StackType.NODE:
        # Grab "name" from package.json (simple regex to avoid json import)
        match = re.search(r'"name"\s*:\s*"([^"]+)"', text)
        return match.group(1) if match else ""

    if stack_type == StackType.PYTHON:
        # pyproject.toml: name = "..."
        match = re.search(r'name\s*=\s*"([^"]+)"', text)
        return match.group(1) if match else ""

    return ""


class DiscoveryEngine:
    """Recursively scans a workspace to detect technology stack signatures.

    Parameters:
        root: The workspace root directory to scan.
        max_depth: Maximum directory depth for recursion (0 = root only).
            Pass ``None`` for unlimited depth.
    """

    def __init__(self, root: Path, *, max_depth: int | None = None) -> None:
        self.root = root.resolve()
        self.max_depth = max_depth

    # -- public API ----------------------------------------------------------

    def scan(self) -> list[StackSignature]:
        """Execute the scan and return all detected signatures."""
        signatures: list[StackSignature] = []
        seen_manifests: set[Path] = set()

        for dirpath_str, dirnames, filenames in os.walk(self.root):
            dirpath = Path(dirpath_str)

            # Depth guard
            if self.max_depth is not None:
                depth = len(dirpath.relative_to(self.root).parts)
                if depth > self.max_depth:
                    dirnames.clear()
                    continue

            # Prune skippable directories (in-place so os.walk won't descend)
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]

            # --- Directory-name rules ---
            for dirname in list(dirnames):
                for pattern, stack_type in _DIR_RULES:
                    if dirname == pattern:
                        full = dirpath / dirname
                        if full not in seen_manifests:
                            seen_manifests.add(full)
                            signatures.append(
                                StackSignature(
                                    manifest_path=full,
                                    stack_type=stack_type,
                                )
                            )

            # --- File-name rules ---
            for filename in filenames:
                for pattern, stack_type, is_regex in _FILE_RULES:
                    matched = (
                        bool(re.match(pattern, filename)) if is_regex else filename == pattern
                    )
                    if matched:
                        full = dirpath / filename
                        if full not in seen_manifests:
                            seen_manifests.add(full)
                            ctx = _extract_context(full, stack_type)
                            signatures.append(
                                StackSignature(
                                    manifest_path=full,
                                    stack_type=stack_type,
                                    context=ctx,
                                )
                            )

        return signatures
