"""Sequencing Layer — ADR Sequence Management.

Handles ID generation, numbering integrity, and concurrency locking.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Optional


class SequenceManager:
    """Manages ADR IDs and prevents collisions.

    Parameters:
        adr_dir: Directory where ADR files are stored.
    """

    def __init__(self, adr_dir: Path) -> None:
        self.adr_dir = adr_dir
        self.lock_file = adr_dir / ".adr.lock"

    def next_id(self) -> str:
        """Calculate the next available zero-padded ID (e.g. "0005")."""
        existing_ids = []
        if self.adr_dir.is_dir():
            for f in self.adr_dir.glob("*.md"):
                match = re.match(r"^(\d{4,})", f.stem)
                if match:
                    existing_ids.append(int(match.group(1)))
                    
        next_val = max(existing_ids, default=0) + 1
        return f"{next_val:04d}"

    def check_integrity(self) -> list[int]:
        """Check for gaps in ADR numbering. Returns a list of missing IDs."""
        existing_ids = []
        if self.adr_dir.is_dir():
            for f in self.adr_dir.glob("*.md"):
                match = re.match(r"^(\d{4,})", f.stem)
                if match:
                    existing_ids.append(int(match.group(1)))
        
        if not existing_ids:
            return []
            
        existing_ids.sort()
        expected_ids = list(range(1, max(existing_ids) + 1))
        return [i for i in expected_ids if i not in existing_ids]

    def acquire_lock(self, timeout: int = 10) -> bool:
        """Simple file-based lock for concurrency protection."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to create the file, fail if it exists (exclusive)
                with open(self.lock_file, "x"):
                    return True
            except FileExistsError:
                time.sleep(0.5)
        return False

    def release_lock(self) -> None:
        """Release the file-based lock."""
        try:
            os.remove(self.lock_file)
        except OSError:
            pass
