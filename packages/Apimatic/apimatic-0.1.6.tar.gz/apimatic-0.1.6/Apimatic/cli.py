from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List, Dict

from Apimatic.detect import autodetect_frameworks
from Apimatic.parsers import get_parser
from Apimatic.generator import generate_markdown
from Apimatic.usedAllAI.ollama import enhance_with_ollama
from Apimatic.usedAllAI.openAI import enhance_with_openai, update_api_key as update_openai_key
from Apimatic.usedAllAI.googleGemini import enhance_with_gemini, update_api_key as update_gemini_key
from Apimatic.usedAllAI.groq import enhance_with_groq, update_api_key as update_groq_key

def handle_generation(args: argparse.Namespace) -> None:
    """Handles the 'generate' command."""
    src = Path(args.src).resolve()
    if not src.exists():
        print(f"❌ Source path not found: {src}")
        sys.exit(2)

    frameworks: List[str] = args.framework or autodetect_frameworks(src)
    if not frameworks:
        print("⚠️ No framework detected. You can force one with --framework <name>.")
        sys.exit(1)

    print(f"🔎 Framework(s): {', '.join(frameworks)}")

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

    # LLM enhancements
    if args.use_ollama:
        try:
            endpoints = enhance_with_ollama(endpoints, model=args.ollama_model)
        except Exception as e:
            print(f"⚠️ Ollama enhancement failed: {e}")
            print("   Guidance: Ensure Ollama is running and the specified model is installed.")

    if args.use_openai:
        try:
            endpoints = enhance_with_openai(endpoints, model=args.openai_model)
        except Exception as e:
            print(f"⚠️ OpenAI enhancement failed: {e}")
            print("   Guidance: Check your internet connection and API key.")
            print("   You can set your key with: apimatic config --set-openai-key YOUR_KEY")

    if args.use_google_gemini:
        try:
            endpoints = enhance_with_gemini(endpoints, model_name=args.google_gemini_model)
        except Exception as e:
            print(f"⚠️ Google Gemini enhancement failed: {e}")
            print("   Guidance: Check your internet connection and API key.")
            print("   You can set your key with: apimatic config --set-gemini-key YOUR_KEY")

    if args.use_groq:
        try:
            endpoints = enhance_with_groq(endpoints, model=args.groq_model)
        except Exception as e:
            print(f"⚠️ Groq enhancement failed: {e}")
            print("   Guidance: Check your internet connection and API key.")
            print("   You can set your key with: apimatic config --set-groq-key YOUR_KEY")

    # Output generation
    if args.format == "markdown":
        try:
            content = generate_markdown(endpoints)
            out = Path(args.output or src / "API_Docs.md")
            out.write_text(content, encoding="utf-8")
            print(f"✅ Wrote Markdown: {out}")
        except Exception as e:
            print(f"⚠️ Markdown generation failed: {e}")

def handle_config(args: argparse.Namespace) -> None:
    """Handles the 'config' command."""
    if args.set_openai_key:
        update_openai_key(args.set_openai_key)
    elif args.set_gemini_key:
        update_gemini_key(args.set_gemini_key)
    elif args.set_groq_key:
        update_groq_key(args.set_groq_key)
    else:
        print("Please specify which key to set, e.g., --set-openai-key")
        sys.exit(1)

def main() -> None:
    p = argparse.ArgumentParser(
        prog="Apimatic",
        description="A tool to automatically generate beautiful API documentation from source code.",
    )
    subparsers = p.add_subparsers(dest="command", required=True)

    # 'generate' command
    gen_p = subparsers.add_parser("generate", help="Generate API documentation.")
    gen_p.add_argument("--src", default=".", help="The root directory of the project to scan.")
    gen_p.add_argument("--framework", nargs="*", default=None, help="Force a specific framework.")
    gen_p.add_argument("--format", choices=["markdown"], default="markdown", help="Output format.")
    gen_p.add_argument("--output", default=None, help="Full path for the output file.")
    gen_p.add_argument("--use-ollama", action="store_true", help="Enhance with Ollama.")
    gen_p.add_argument("--ollama-model", default="phi3:mini", help="Ollama model to use.")
    gen_p.add_argument("--use-openai", action="store_true", help="Enhance with OpenAI.")
    gen_p.add_argument("--openai-model", default="gpt-4o-mini", help="OpenAI model to use.")
    gen_p.add_argument("--use-google-gemini", action="store_true", help="Enhance with Google Gemini.")
    gen_p.add_argument("--google-gemini-model", default="gemini-1.5-flash", help="Google Gemini model.")
    gen_p.add_argument("--use-groq", action="store_true", help="Enhance with Groq.")
    gen_p.add_argument("--groq-model", default="llama3-8b-8192", help="Groq model to use.")
    gen_p.set_defaults(func=handle_generation)

    # 'config' command
    config_p = subparsers.add_parser("config", help="Configure API keys.")
    config_p.add_argument("--set-openai-key", help="Set the OpenAI API key.")
    config_p.add_argument("--set-gemini-key", help="Set the Google Gemini API key.")
    config_p.add_argument("--set-groq-key", help="Set the Groq API key.")
    config_p.set_defaults(func=handle_config)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
