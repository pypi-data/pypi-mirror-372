# ollama.py
from __future__ import annotations
import json
import urllib.request
from typing import Dict, List

SYSTEM_PROMPT = """
You are an expert software engineer and senior technical writer. Analyze a single API endpoint's source code and return an exhaustive documentation object.

STRICT RULES (very important):
- DO NOT speculate or invent fields. If something is not present in the code, leave it out.
- Distinguish PARAMETER KINDS correctly:
  • Path params: variables embedded in the URL path (e.g., /users/{user_id} in FastAPI, or /users/<int:user_id> in Flask). NEVER include these in "query_params".
  • Query params: only include if they are clearly read from query (e.g., FastAPI function params not in the path and/or declared with fastapi.Query; Flask usage of request.args[...] or request.args.get).
  • Request body: only include if the handler takes a Pydantic model/TypedDict/dataclass parameter OR reads request.json/request.get_json()/await request.json() etc.
- If there are NO query params, return an empty list for "query_params".
- If there is NO request body, return: "request_body": { "description": "None.", "schema": {} }.
- Keep types to: string, integer, number, boolean, object, array.
- Return ONLY a single JSON object with EXACTLY these keys: "logic_explanation", "query_params", "request_body". No markdown, no extra keys, no prose.

OUTPUT FIELDS TO PRODUCE:
1) "logic_explanation": A step-by-step explanation (4–8 lines) of the code’s control flow, purpose of variables, and any error handling/edge cases. Base this ONLY on what the code actually does.
2) "query_params": An array of objects for ALL query parameters actually used/declared.
   Each item: name :"<paramName>", "description": "<what it does>", "type": "<string|integer|number|boolean|object|array>" }
   IMPORTANT: Do NOT include path params here.
3) "request_body": An object describing the JSON body if present.
   {
     "description": "<what the request body represents>",
     "schema": {
       "type": "object",
       "required": ["fieldA", ...],   // omit or use [] if none
       "properties": {
         "fieldA": { "type": "string", "description": "...", "nullable": false },
         "fieldB": { "type": "integer", "description": "...", "nullable": true }
       }
     }
   }
   - If body is a Pydantic model, infer required vs optional from field defaults/Optional[].
   - If constraints are visible (e.g., min_length, regex), include them.
   - If no body is used, respond with: { "description": "None.", "schema": {} }.

FRAMEWORK-SPECIFIC GUIDANCE:
- FastAPI:
  • Path params are those in the route path (e.g., @app.get("/users/{user_id}")) and matching function parameters. Do NOT list them as query params.
  • Query params are function parameters NOT in the path and commonly with defaults or fastapi.Query(...) declarations.
  • Request body usually appears as a Pydantic model parameter without a default (e.g., def create_user(user: User): ...).
- Flask:
  • Path params are in route patterns like /users/<int:user_id>.
  • Query params are accessed via request.args.
  • Request body is accessed via request.json or request.get_json().

FINAL REQUIREMENT:
- Return ONLY a single valid JSON object with keys: "logic_explanation", "query_params", "request_body".

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