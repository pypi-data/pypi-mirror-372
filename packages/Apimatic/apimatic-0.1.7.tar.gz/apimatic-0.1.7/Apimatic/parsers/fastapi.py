from __future__ import annotations
import ast
from pathlib import Path
from typing import List, Dict

from Apimatic.utils import iter_files

def parse_fastapi_routes(src: Path) -> List[Dict]:
    endpoints: List[Dict] = []
    for file in iter_files(src, exts=(".py",)):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
            
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue

                for decorator in node.decorator_list:
                    # Look for decorators like @app.get, @app.post, @router.get, etc.
                    if (isinstance(decorator, ast.Call) and
                        isinstance(decorator.func, ast.Attribute) and
                        isinstance(decorator.func.value, ast.Name) and
                        decorator.func.attr.upper() in ("GET", "POST", "PUT", "DELETE", "PATCH") and
                        decorator.func.value.id in ("app", "router")):
                        
                        method = decorator.func.attr.upper()
                        
                        # Get the path from the first argument of the decorator
                        path = ""
                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                            path = decorator.args[0].value
                        
                        # Extract the source code for the decorated function
                        source_code = ast.get_source_segment(text, node)

                        endpoints.append({
                            "framework": "fastapi",
                            "file": str(file.relative_to(src)),
                            "method": method,
                            "path": path,
                            "source": source_code,
                            "summary": f"{method} {path}"
                        })
        except (SyntaxError, UnicodeDecodeError):
            # Skip files that have syntax errors or are not correctly encoded
            continue
            
    return endpoints