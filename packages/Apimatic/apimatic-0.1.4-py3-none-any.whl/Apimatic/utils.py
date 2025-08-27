from __future__ import annotations
from pathlib import Path
from typing import Iterable, Tuple
import subprocess

def iter_files(root: Path, exts: Tuple[str, ...]) -> Iterable[Path]:
    root = Path(root)
    
    cmd = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    
    if result.returncode != 0:
        # Fallback to rglob if git is not available or not a git repository
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in exts:
                yield p
        return

    for line in result.stdout.splitlines():
        p = root / line
        if p.is_file() and p.suffix in exts:
            yield p
