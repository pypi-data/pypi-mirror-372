from __future__ import annotations
import json
from typing import Dict, List

def generate_markdown(endpoints: List[Dict]) -> str:
    """
    Generates a Markdown string for comprehensive API documentation
    from a list of endpoint dictionaries.
    """
    # Sort by framework first for logical grouping, then by path+method
    endpoints.sort(key=lambda x: (x.get("framework", "other"), x.get("path", ""), x.get("method", "")))
    
    out = ["# API Documentation\n"]
    current_group = None

    for ep in endpoints:
        group = ep.get("framework", "other")
        if group != current_group:
            out.append(f"\n## {group.title()} API Endpoints\n")
            current_group = group

        title = ep.get('summary') or f"{ep.get('method','ANY')} {ep.get('path','/')}"
        out.append(f"\n### `{title}`\n")
        out.append(f"- **Endpoint:** `{ep.get('method','ANY')} {ep.get('path','/')}`\n")
        out.append(f"- **Source File:** `{ep.get('file','?')}`\n")

        # Extract and format data from the JSON object returned by Ollama
        api_details = ep.get('ai_details', {})
        
        # 1. Logic Explanation
        logic_explanation = api_details.get('logic_explanation')
        if isinstance(logic_explanation, str) and logic_explanation.strip():
            out.append(f"- **Logic Explanation:**\n")
            lines = logic_explanation.splitlines()
            for line in lines:
                line = line.strip()
                if line:  # skip empty lines
                    out.append(f"   - {line}\n")


        # 2. Source Code
        source = ep.get("source")
        if source:
            lang = "javascript" if ep.get("framework") == "express" else "python"
            out.append("- **Source Code:**\n")
            out.append(f'```{lang}\n{source.strip()}\n```\n')

        # 3. Query Params
        query_params = api_details.get("query_params", [])
        out.append("- **Query Params:**\n")
        if query_params:
            out.append("\n")
            out.append("| Name | Description | Type |\n")
            out.append("|------|-------------|------|\n")
            for param in query_params:
                out.append(f"| `{param.get('name', '')}` | {param.get('description', '')} | {param.get('type', '')} |\n")
        else:
            out.append("  _None_\n")

        # 4. Request Body
        request_body = api_details.get("request_body", {})
        out.append("- **Request Body:**\n")
        if request_body:
            if request_body.get("description"):
                out.append(f"  {request_body['description']}\n")
            if request_body.get("schema"):
                schema_json = json.dumps(request_body.get("schema", {}), indent=2)
                out.append(f'```json\n{schema_json}\n  ```\n')
        else:
            out.append("  _None_\n")        
    return "".join(out)