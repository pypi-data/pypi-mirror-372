from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict

from Apimatic.utils import iter_files

# This regex is more robust.
# It captures the HTTP method, path, and the function handler's content.
# It handles single-line and multi-line definitions.
ROUTE_RE = re.compile(
    r"""
    \b(?:app|router)\.
    (get|post|put|delete|patch|use|all)
    \s*\(\s*
    ['"`]([^'"`]+)['"`]
    (?:,\s*
    (
        # Matches a full function, including arrow functions, named functions, or arrays of handlers
        (?:
            # Match an array of handlers
            \[[\s\S]*?\]
            |
            # Match a named function
            \b[a-zA-Z_]\w*\b
            |
            # Match a full function definition (async or not, arrow or not)
            (?:async\s+)?
            (?:function\s+\w+\s*)?
            \([\s\S]*?\)
            \s*
            =>\s*
            \{[\s\S]*?\}
            |
            (?:async\s+)?
            function\s*\w*\s*\([\s\S]*?\)
            \s*\{[\s\S]*?\}
        )
    ))
    """,
    re.VERBOSE | re.MULTILINE
)

def parse_express_routes(src: Path) -> List[Dict]:
    endpoints: List[Dict] = []
    for file in iter_files(src, exts=(".js", ".ts")):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            
            # Find all route matches in the file
            for match in ROUTE_RE.finditer(text):
                method, path, source = match.groups()
                
                if source is None:
                    # This case handles middleware routes like app.use('/api', router);
                    # We can't get a source for a full router, so we skip it.
                    continue

                # Clean up the source code for a better look
                cleaned_source = source.strip()

                endpoints.append({
                    "framework": "express",
                    "file": str(file.relative_to(src)),
                    "method": method.upper(),
                    "path": path,
                    "source": cleaned_source,
                    "summary": f"{method.upper()} {path}"
                })
        except Exception:
            # Continue to the next file if an error occurs
            continue
            
    return endpoints