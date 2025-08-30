from __future__ import annotations
import json
from typing import Dict, List, Optional


def generate_markdown(endpoints: List[Dict]) -> str:
    """
    Generates a Markdown string for comprehensive API documentation.

    Each endpoint dictionary may include:
      - framework: str (e.g., "express", "flask")
      - method: str (HTTP method)
      - path: str (route path)
      - file: str (source file path)
      - handlers: List[str] (multiple handler sources or names)
      - source: str (legacy single handler source)
      - summary: str (short description)
      - ai_details: Dict (optional LLM-enriched metadata), which may contain:
        • logic_explanation: str
        • query_params: List[Dict{name, description, type}]
        • request_body: Dict{description, schema}
    """
    # ---- Sort endpoints for consistent grouping ----
    endpoints.sort(
        key=lambda ep: (
            ep.get("framework", "other"),
            ep.get("path", ""),
            ep.get("method", ""),
        )
    )

    out: List[str] = ["# API Documentation\n"]
    current_framework: Optional[str] = None

    for ep in endpoints:
        framework = ep.get("framework", "other").title()
        method = ep.get("method", "ANY").upper()
        path = ep.get("path", "/")
        summary = ep.get("summary") or f"{method} {path}"
        file = ep.get("file", "?")
        handlers = ep.get("handlers")  # new style
        source = ep.get("source")      # legacy
        api_details = ep.get("ai_details", {}) or {}

        # ---- Group heading per framework ----
        if framework != current_framework:
            out.append(f"\n## {framework} API Endpoints\n")
            current_framework = framework

        # ---- Endpoint title ----
        out.append(f"\n### `{summary}`\n")
        out.append(f"- **Endpoint:** `{method} {path}`\n")
        out.append(f"- **Source File:** `{file}`\n")

        # ---- Logic explanation (AI-enhanced) ----
        logic_explanation = api_details.get("logic_explanation")
        if isinstance(logic_explanation, str) and logic_explanation.strip():
            out.append("- **Logic Explanation:**\n")
            for line in logic_explanation.splitlines():
                line = line.strip()
                if line:
                    out.append(f"  - {line}\n")

        # ---- Handlers (multiple) ----
        if handlers and isinstance(handlers, list):
            out.append("- **Handlers:**\n")
            lang = "javascript" if ep.get("framework") == "express" else "python"
            for idx, handler in enumerate(handlers, start=1):
                label = f"Handler {idx}"
                out.append(f"  - {label}:\n")
                if "\n" in handler or "{" in handler:  # looks like code
                    out.append(f"```{lang}\n{handler.strip()}\n```\n")
                elif handler.strip():
                    out.append(f"    `{handler.strip()}`\n")

        # ---- Legacy single source ----
        elif source:
            lang = "javascript" if ep.get("framework") == "express" else "python"
            out.append("- **Source Code:**\n")
            out.append(f"```{lang}\n{source.strip()}\n```\n")

        # ---- Query params ----
        query_params = api_details.get("query_params", []) or []
        out.append("- **Query Params:**\n")
        if query_params:
            out.append("\n| Name | Description | Type |\n")
            out.append("|------|-------------|------|\n")
            for param in query_params:
                out.append(
                    f"| `{param.get('name','')}` | "
                    f"{param.get('description','') or '_No description_'} | "
                    f"`{param.get('type','')}` |\n"
                )
        else:
            out.append("  _None_\n")

        # ---- Request body ----
        request_body = api_details.get("request_body") or {}
        out.append("- **Request Body:**\n")

        desc = request_body.get("description") if isinstance(request_body, dict) else None
        schema = request_body.get("schema") if isinstance(request_body, dict) else None

        if desc and desc.lower() != "none.":
            out.append(f"  {desc}\n")
        elif not desc or desc.lower() == "none.":
            out.append("  _None_\n")

        if schema and isinstance(schema, dict) and schema:
            schema_json = json.dumps(schema, indent=2)
            out.append(f"```json\n{schema_json}\n```\n")

    return "".join(out)