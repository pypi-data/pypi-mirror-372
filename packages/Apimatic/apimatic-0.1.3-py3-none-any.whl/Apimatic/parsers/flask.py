from __future__ import annotations
import ast
from pathlib import Path
from typing import List, Dict

from Apimatic.utils import iter_files

def parse_flask_routes(src: Path) -> List[Dict]:
    endpoints: List[Dict] = []
    for file in iter_files(src, exts=(".py",)):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)

            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue

                for decorator in node.decorator_list:
                    if not (isinstance(decorator, ast.Call) and 
                            isinstance(decorator.func, ast.Attribute) and
                            decorator.func.attr == 'route'):
                        continue

                    path = ""
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value

                    methods = ["GET"]
                    for keyword in decorator.keywords:
                        if keyword.arg == 'methods' and isinstance(keyword.value, (ast.List, ast.Tuple)):
                            methods = [el.value for el in keyword.value.elts if isinstance(el, ast.Constant)]

                    source_code = ast.get_source_segment(text, node)

                    for method in methods:
                        endpoints.append({
                            "framework": "flask",
                            "file": str(file.relative_to(src)),
                            "method": method.upper(),
                            "path": path,
                            "source": source_code,
                            "summary": f"{method.upper()} {path}"
                        })
        except (SyntaxError, UnicodeDecodeError):
            continue
            
    return endpoints
