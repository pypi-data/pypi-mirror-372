from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import List, Dict, Optional

from Apimatic.utils import iter_files

# This regex is slightly more robust to handle additional arguments in the path() function
PATH_RE = re.compile(r"""\bpath\(\s*['"]([^'" ]+)['"],\s*([\w\.]+)(?:\.as_view\(\))?\s*.*\)""", re.VERBOSE)

def get_source_from_views_file(views_file: Path, view_name: str) -> Optional[str]:
    """Finds and returns the source code for a specific view function or class."""
    if not views_file.exists():
        return None
    try:
        text = views_file.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(text)
        for node in ast.walk(tree):
            # Check for both function and class definitions that match the view name
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == view_name:
                return ast.get_source_segment(text, node)
    except Exception:
        # Silently fail on parsing errors for robust scanning
        return None
    return None

def get_methods_from_class_source(source: str) -> List[str]:
    """Inspects a class's source code to find HTTP methods (get, post, etc.)."""
    methods = []
    try:
        tree = ast.parse(source)
        # The ast.parse will wrap the code in a Module, so we check the first item in the body
        class_node = tree.body[0]
        if isinstance(class_node, ast.ClassDef):
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef) and node.name.lower() in ["get", "post", "put", "patch", "delete"]:
                    methods.append(node.name.upper())
    except Exception:
        pass
    # If no specific methods are found, it's likely a generic view that handles all methods,
    # or an error occurred.
    return methods if methods else ["ANY"]

def parse_django_routes(src: Path) -> List[Dict]:
    """
    Parses Django URL configuration files to extract API endpoints.
    This function assumes a standard Django app structure where urls.py and views.py
    are in the same directory.
    """
    endpoints: List[Dict] = []
    for urls_file in iter_files(src, exts=(".py",)):
        views_file = urls_file.parent / "views.py"
        try:
            text = urls_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for match in PATH_RE.finditer(text):
            path, view_str = match.groups()
            view_name = view_str.split(".")[-1]

            source = get_source_from_views_file(views_file, view_name)
            if not source:
                continue

            methods = get_methods_from_class_source(source)
            for method in methods:
                endpoints.append({
                    "framework": "django",
                    "file": str(views_file.relative_to(src)),
                    "method": method,
                    "path": "/" + path.strip("/"),
                    "source": source,
                    "summary": f"{method} /{path.strip('/')}"
                })

    return endpoints