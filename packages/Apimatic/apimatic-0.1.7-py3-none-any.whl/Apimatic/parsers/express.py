from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Tuple

from Apimatic.utils import iter_files

# Regex to find the start of an Express route, capturing the handler as a variable name or an inline function start
ROUTE_RE = re.compile(
    r"""\b(?:app|router)\.(get|post|put|delete|patch|all)\s*\(\s*['"`]([^'"`]+)['"`]\s*,\s*(?:async\s+)?(.*?)\s*\)?[,;]?\s*$""",
    re.MULTILINE
)

def find_function_body(text: str, start_pos: int) -> Tuple[str | None, int]:
    """Finds the body of a function starting from a given position by matching braces."""
    try:
        open_brace_pos = text.find("{", start_pos)
        if open_brace_pos == -1:
            return None, -1

        brace_level = 1
        current_pos = open_brace_pos + 1
        while current_pos < len(text) and brace_level > 0:
            if text[current_pos] == "{":
                brace_level += 1
            elif text[current_pos] == "}":
                brace_level -= 1
            current_pos += 1

        if brace_level == 0:
            return text[open_brace_pos:current_pos], current_pos
        return None, -1
    except IndexError:
        return None, -1

def find_named_function_source(text: str, func_name: str) -> str | None:
    """Finds the full source code of a named function in the text."""
    # Regex to find function definition (handles `function name(...)` and `const name = (...) =>`)
    func_def_re = re.compile(
        r"""(?:function\s+{func_name}\s*\(|(?:const|let|var)\s+{func_name}\s*=\s*(?:async\s*)?\()"""
    )
    match = func_def_re.search(text)
    if not match:
        return None

    body_start = match.end() - 1 # Start from the opening parenthesis
    
    # Find the full function signature by matching parentheses
    paren_level = 1
    sig_end = body_start + 1
    while sig_end < len(text) and paren_level > 0:
        if text[sig_end] == '(':
            paren_level += 1
        elif text[sig_end] == ')':
            paren_level -= 1
        sig_end += 1
    
    if paren_level != 0:
        return None # Malformed signature

    # Find the function body
    body, _ = find_function_body(text, sig_end)
    if not body:
        return None

    return text[match.start():sig_end] + body

def parse_express_routes(src: Path) -> List[Dict]:
    """Parses all Express.js routes from files in the source directory."""
    endpoints: List[Dict] = []
    for file in iter_files(src, exts=(".js", ".ts")):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            
            for i, line in enumerate(lines):
                match = ROUTE_RE.match(line.strip())
                if not match:
                    continue

                method, path, handler_str = match.groups()
                handler_str = handler_str.strip()
                source = None

                if handler_str.startswith("function") or handler_str.startswith("(") or handler_str.startswith("async"):
                    # It's an inline anonymous or arrow function
                    full_line_pos = text.find(line)
                    handler_start_pos = full_line_pos + line.find(handler_str)
                    
                    # Find signature
                    paren_level = 0
                    sig_end = 0
                    in_string = False
                    for j, char in enumerate(text[handler_start_pos:]):
                        if char in ['" ', "`"]:
                            in_string = not in_string
                        if not in_string:
                            if char == '(':
                                paren_level += 1
                            elif char == ')':
                                paren_level -= 1
                                if paren_level == 0:
                                    sig_end = handler_start_pos + j + 1
                                    break
                    if not sig_end:
                        continue

                    body, _ = find_function_body(text, sig_end)
                    if body:
                        source = text[handler_start_pos:sig_end] + body

                elif re.match(r"^[a-zA-Z_][\w]*$", handler_str):
                    # It's a named function reference
                    source = find_named_function_source(text, handler_str)

                if source:
                    endpoints.append({
                        "framework": "express",
                        "file": str(file.relative_to(src)),
                        "method": method.upper(),
                        "path": path,
                        "source": source.strip(),
                        "summary": f"{method.upper()} {path}"
                    })
        except Exception:
            continue
            
    return endpoints
