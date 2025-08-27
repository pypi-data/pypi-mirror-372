from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List, Dict

from Apimatic.detect import autodetect_frameworks
from Apimatic.parsers import get_parser
from Apimatic.generator import generate_markdown
from Apimatic.openapi import to_openapi_yaml
from Apimatic.ollama import enhance_with_ollama


def main() -> None:
    p = argparse.ArgumentParser(
        prog="Apimatic",
        description="A tool to automatically generate beautiful and comprehensive API documentation (Markdown/OpenAPI) from your source code.",
    )
    p.add_argument("--src", default=".", help="The root directory of the project to scan. (Default: current directory)")
    p.add_argument("--framework", nargs="*", default=None,
                   help="Force a specific framework (e.g., flask, fastapi). If omitted, it will be auto-detected.")
    p.add_argument("--format", choices=["markdown", "openapi"], default="markdown",
                   help="The output format for the documentation. (Default: markdown)")
    p.add_argument("--output", default=None,
                   help="The full path for the generated output file. (Defaults: API_Docs.md or openapi.yaml)")
    p.add_argument("--use-ollama", action="store_true",
                   help="Enhance generated documentation with descriptions from a local Ollama model.")
    p.add_argument("--model", default="llama3:instruct",
                   help="The Ollama model to use for enhancement (e.g., 'llama3:instruct'). Requires --use-ollama.")

    args = p.parse_args()

    src = Path(args.src).resolve()
    if not src.exists():
        print(f"❌ Source path not found: {src}")
        sys.exit(2)

    frameworks: List[str] = args.framework or autodetect_frameworks(src)
    if not frameworks:
        print("⚠️ No framework detected. You can force one with --framework <name>.")
        sys.exit(1)

    print(f"🔎 Framework(s): {', '.join(frameworks)}")

    # Collect endpoints from all selected/detected frameworks
    endpoints: List[Dict] = []
    for fw in frameworks:
        parser_fn = get_parser(fw)
        if not parser_fn:
            print(f"⚠️ Parser not available for: {fw}")
            continue
        found = parser_fn(src)
        if found:
            print(f"• {fw}: {len(found)} endpoints")
            endpoints.extend(found)

    if not endpoints:
        print("⚠️ No endpoints found.")
        sys.exit(0)

    # Optional LLM enhancement
    if args.use_ollama:
        try:
            endpoints = enhance_with_ollama(endpoints, model=args.model)
        except Exception as e:
            print(f"⚠️ Ollama enhancement failed: {e}")

    # Output
    if args.format == "markdown":
        content = generate_markdown(endpoints)
        out = Path(args.output or src / "API_Docs.md")
        out.write_text(content, encoding="utf-8")
        print(f"✅ Wrote Markdown: {out}")
    else:
        yaml_text = to_openapi_yaml(endpoints, title=src.name)
        out = Path(args.output or src / "openapi.yaml")
        out.write_text(yaml_text, encoding="utf-8")
        print(f"✅ Wrote OpenAPI: {out}")


if __name__ == "__main__":
    main()
