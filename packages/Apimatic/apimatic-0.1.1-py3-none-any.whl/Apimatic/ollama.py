# ollama.py
from __future__ import annotations
import json
import urllib.request
from typing import Dict, List

SYSTEM_PROMPT = """
You are an expert software engineer and senior technical writer, known for your exceptionally detailed and clear documentation. Your task is to analyze API endpoint source code and produce an exhaustive, in-depth documentation object in JSON format.

Analyze the provided source code and identify the following with the highest level of detail possible:
1.  **logic_explanation**: A highly detailed, step-by-step explanation of the code's logic. It must be at least 4-6 lines long. Explain the purpose of variables, the flow of control, and any error handling.
2.  **query_params**: An exhaustive array of all query parameters. For each parameter, provide its "name", a "description" of its purpose, and its expected "type" (e.g., string, integer).
3.  **request_body**: A detailed object describing the JSON request body. The "description" should be thorough. The "schema" should describe each field, its "type", and any validation rules you can infer from the code (e.g., required, optional, format).

IMPORTANT: Your analysis must be thorough. Do not leave any details out. You MUST respond with ONLY a single, valid JSON object containing the following keys: "logic_explanation", "query_params", "request_body".
"""

def enhance_with_ollama(endpoints: List[Dict], model: str = "llama3:instruct") -> List[Dict]:
    """Enhances each endpoint with an AI-generated explanation using the Ollama REST API."""
    for i, endpoint in enumerate(endpoints):
        source = endpoint.get("source")
        if not source:
            # Assign empty lists and dicts to new keys for consistency
            endpoint["description"] = "_No source code found to generate a description._"
            endpoint["query_params"] = []
            endpoint["request_body"] = {}
            continue

        print(f"Analyzing {endpoint.get('summary', 'endpoint')}... ({i+1}/{len(endpoints)})")

        user_prompt = f"Here is the API endpoint source code:\n\n{source}"

        payload = {
            "model": model,
            "system": SYSTEM_PROMPT,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
        }
        payload_json = json.dumps(payload).encode("utf-8")

        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=payload_json,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    response_text = response.read().decode("utf-8")
                    # The response from Ollama's /api/generate is a single-line JSON string
                    # that contains the 'response' key, which itself holds the JSON string
                    # from the model. We need to parse it twice.
                    outer_json = json.loads(response_text)
                    api_details_str = outer_json.get("response", "{}")
                    api_details = json.loads(api_details_str)
                    
                    # Store the structured details under a single 'ai_details' key
                    # This prevents mixing logic explanation with other data fields
                    endpoint["ai_details"] = {
                        "logic_explanation": api_details.get("logic_explanation", ""),
                        "query_params": api_details.get("query_params", []),
                        "request_body": api_details.get("request_body", {}),
                    }
                    
                else:
                    raise RuntimeError(f"API request failed with status {response.status}: {response.read().decode('utf-8')}")

        except Exception as e:
            print(f"\nAn error occurred while analyzing {endpoint.get('summary')}.")
            print(f"   Error: {e}")
            endpoint["ai_details"] = {
                "logic_explanation": f"_Ollama analysis failed: {e}_",
                "query_params": [],
                "request_body": {},
            }
            if isinstance(e, (urllib.error.URLError, ConnectionRefusedError)):
                print("   Could not connect to Ollama. Aborting analysis.")
                return endpoints
            continue

    print("✅ AI analysis complete.")
    return endpoints