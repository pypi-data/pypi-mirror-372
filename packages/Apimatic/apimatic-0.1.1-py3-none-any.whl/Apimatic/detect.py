from __future__ import annotations
from pathlib import Path
from typing import List


PY_HINTS = {
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "django": ["Django", "django", "djangorestframework"],
}

JS_HINTS = {
    "express": ["express"],
    # future: koa, hapi, nest, etc.
}


def _read_text_if_exists(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def _detect_from_requirements(root: Path) -> List[str]:
    out: List[str] = []
    current_path = root
    while current_path != current_path.parent:
        txt = _read_text_if_exists(current_path / "requirements.txt")
        pyproj = _read_text_if_exists(current_path / "pyproject.toml")
        for fw, toks in PY_HINTS.items():
            if txt and any(t in txt for t in toks):
                out.append(fw)
            elif pyproj and any(t in pyproj for t in toks):
                out.append(fw)
        if out:
            return out
        current_path = current_path.parent
    return out


def _detect_from_package_json(root: Path) -> List[str]:
    out: List[str] = []
    pkg = _read_text_if_exists(root / "package.json")
    for fw, toks in JS_HINTS.items():
        if pkg and any(t in pkg for t in toks):
            out.append(fw)
    return out


def autodetect_frameworks(root: Path) -> List[str]:
    found = set()
    for fw in _detect_from_requirements(root):
        found.add(fw)
    for fw in _detect_from_package_json(root):
        found.add(fw)
    return sorted(found)
