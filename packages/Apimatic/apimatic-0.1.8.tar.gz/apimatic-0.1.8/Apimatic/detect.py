from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Tuple
import json
import tomllib
import functools

# =======================
# Framework Signature Hints
# =======================
FRAMEWORK_HINTS: Dict[str, Dict[str, List[str]]] = {
    "python": {
        "flask": ["flask"],
        "fastapi": ["fastapi"],
        "django": ["django", "djangorestframework"],
    },
    "javascript": {
        "express": ["express"],
        "koa": ["koa"],
        "nest": ["@nestjs/core"],
    },
    # easy to extend: add php, ruby, go, etc.
}


# =======================
# File Readers with Caching
# =======================
@functools.lru_cache(maxsize=None)
def _read_text_if_exists(p: Path) -> str:
    """Read a text file safely with UTF-8 encoding, or return '' if not exists."""
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


# =======================
# Detection Functions
# =======================
def _detect_python_frameworks(root: Path) -> List[Tuple[str, int]]:
    """
    Detect Python frameworks by scanning common dependency files.
    Returns list of (framework, confidence_score).
    """
    confidence: List[Tuple[str, int]] = []
    search_files = ["requirements.txt", "pyproject.toml", "Pipfile", "setup.py"]

    current_path = root
    while current_path != current_path.parent:
        for file in search_files:
            txt = _read_text_if_exists(current_path / file)
            if not txt:
                continue
            for fw, toks in FRAMEWORK_HINTS["python"].items():
                score = sum(txt.count(tok) for tok in toks)
                if score:
                    confidence.append((fw, score))
        if confidence:
            return confidence
        current_path = current_path.parent
    return confidence


def _detect_js_frameworks(root: Path) -> List[Tuple[str, int]]:
    """
    Detect JS frameworks by checking package.json dependencies.
    """
    confidence: List[Tuple[str, int]] = []
    pkg_txt = _read_text_if_exists(root / "package.json")
    if not pkg_txt:
        return confidence

    try:
        pkg = json.loads(pkg_txt)
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    except Exception:
        deps = {}

    for fw, toks in FRAMEWORK_HINTS["javascript"].items():
        for tok in toks:
            if tok in deps:
                confidence.append((fw, 10))  # strong signal if listed directly
            elif tok in pkg_txt:
                confidence.append((fw, 5))  # weaker if just in text
    return confidence


# =======================
# Main Auto-detect Function
# =======================
def autodetect_frameworks(root: Path) -> List[str]:
    """
    Auto-detect frameworks with confidence scoring.
    Returns a sorted list of most likely frameworks.
    """
    found: Dict[str, int] = {}

    for fw, score in _detect_python_frameworks(root):
        found[fw] = found.get(fw, 0) + score

    for fw, score in _detect_js_frameworks(root):
        found[fw] = found.get(fw, 0) + score

    # Sort by confidence (high to low)
    return [fw for fw, _ in sorted(found.items(), key=lambda x: x[1], reverse=True)]
