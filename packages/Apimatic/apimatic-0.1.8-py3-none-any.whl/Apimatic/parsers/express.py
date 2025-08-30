from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Optional, Iterable, Tuple


def iter_files(src: Path, exts: Iterable[str]) -> Iterable[Path]:
    """
    Recursively iterates through files in a source directory with specific extensions.
    
    Args:
        src (Path): The root directory to search.
        exts (Iterable[str]): A list of file extensions to include (e.g., [".js", ".ts"]).
        
    Returns:
        Iterable[Path]: An iterator yielding pathlib.Path objects for each matching file.
    """
    for ext in exts:
        yield from src.rglob(f"*{ext}")

# Matches the start of a route definition, like app.get('/path', ...handlers...)
ROUTE_START_RE = re.compile(
    r"""\b(?:app|router)\.(get|post|put|delete|patch|all)\s* # method (e.g., get, post)
        \(\s*['"`]([^'"`]+)['"`]\s*,\s* # path (e.g., /users/:id)
    """,
    re.VERBOSE,
)


def find_full_handler_sources(text: str, start_pos: int) -> List[str]:
    """
    Extracts the source code for valid handlers within a route definition.
    Handles both inline function handlers and named function references.
    
    Args:
        text (str): The full source code of the file.
        start_pos (int): The starting position to search for handlers, right after the route path.
        
    Returns:
        List[str]: A list of strings, each containing the source code or name of a handler.
    """
    handlers: List[str] = []
    remaining_text = text[start_pos:]
    current_pos = 0

    while current_pos < len(remaining_text):
        # Remove leading whitespace to find the start of the next handler
        trimmed_text = remaining_text[current_pos:].lstrip()
        
        # Check for the end of the route definition
        if not trimmed_text or trimmed_text.startswith(")") or trimmed_text.startswith(";"):
            break

        # Skip a comma if it's separating handlers
        if trimmed_text.startswith(","):
            current_pos += 1
            continue

        # Check for inline handlers (arrow functions or function declarations)
        if trimmed_text.startswith(("(", "async", "function")):
            handler_source = _extract_function_like(trimmed_text)
            if handler_source:
                handlers.append(handler_source.strip())
                current_pos += len(handler_source)
                continue
            else:
                # If a function-like pattern is detected but parsing fails,
                # it's likely not a valid handler. Advance by one to avoid an infinite loop.
                current_pos += 1
                continue

        # Check for named handlers (variable names)
        name_match = re.match(r"^([a-zA-Z_]\w*)", trimmed_text)
        if name_match:
            handler_name = name_match.group(1)
            name_len = len(handler_name)

            # Ignore common, single-letter, or reserved keywords to avoid false positives.
            # This is a heuristic to prevent common variable names from being mistaken for handlers.
            if name_len == 1 or handler_name in {"req", "res", "next", "console", "router", "app"}:
                current_pos += name_len
                continue

            # Attempt to find the full source of the named function
            function_source = find_named_function_source(text, handler_name)
            if function_source:
                handlers.append(function_source.strip())
            else:
                # If the full source can't be found, treat it as a named reference.
                handlers.append(handler_name)
            
            current_pos += name_len
            continue

        # Move to the next character if no handler was matched
        current_pos += 1

    return handlers


def _extract_function_like(substring: str) -> Optional[str]:
    """Extracts inline function or arrow function source code from a substring."""
    try:
        # ---- Match function signature (parentheses) ----
        paren_level, sig_end = 0, -1
        for i, char in enumerate(substring):
            if char == "(":
                paren_level += 1
            elif char == ")":
                paren_level -= 1
                if paren_level == 0:
                    sig_end = i + 1
                    break
        if sig_end == -1:
            return None

        # ---- Match function body (curly braces) ----
        body_start = substring.find("{", sig_end)
        if body_start == -1:
            return None

        brace_level, body_end = 1, -1
        for i, char in enumerate(substring[body_start + 1:], start=body_start + 1):
            if char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1
                if brace_level == 0:
                    body_end = i + 1
                    break

        return substring[:body_end] if body_end != -1 else None
    except IndexError:
        return None


def find_named_function_source(text: str, func_name: str) -> Optional[str]:
    """Finds the full source of a named function declaration or arrow function assignment."""
    func_def_re = re.compile(
        rf"""
        (?:function\s+{func_name}\s*\(                      # function funcName(...)
        |(?:\s*const|let|var)\s+{func_name}\s*=\s*(?:async\s*)? # const funcName = async (...)
        )
        """,
        re.VERBOSE,
    )
    match = func_def_re.search(text)
    return _extract_function_like(text[match.end():]) if match else None


def parse_express_routes(src: Path) -> List[Dict]:
    """
    Parses all Express.js routes from .js/.ts files under a source directory.
    Returns a list of endpoint dictionaries, each potentially containing multiple handlers.
    
    Args:
        src (Path): The root directory to search for source files.
        
    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents an API endpoint.
    """
    endpoints: List[Dict] = []

    # The iter_files function is now defined above to correctly handle file iteration.
    for file in iter_files(src, exts=(".js", ".ts")):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for match in ROUTE_START_RE.finditer(text):
            method, path = match.groups()
            handlers = find_full_handler_sources(text, match.end())
            if not handlers:
                continue

            endpoints.append({
                "framework": "express",
                "file": str(file.relative_to(src)),
                "method": method.upper(),
                "path": path,
                "handlers": handlers,
                "source": "\n\n".join(handlers),
                "summary": f"{method.upper()} {path}",
            })

    return endpoints
