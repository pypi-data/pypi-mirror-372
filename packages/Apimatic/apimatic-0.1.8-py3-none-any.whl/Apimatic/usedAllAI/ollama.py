from __future__ import annotations
import json
import urllib.request
from typing import Dict, List

SYSTEM_PROMPT = """
You are an expert software engineer and senior technical writer. Your task is to analyze the provided source code for a single API endpoint and generate a JSON object that accurately documents its functionality, parameters, and request body.

Your response MUST be a valid JSON object that strictly adheres to the following schema. DO NOT include any additional text or markdown outside of the JSON block.

Schema:
```json
{
 "type": "object",
 "properties": {
   "logic_explanation": {
     "type": "string",
     "description": "Provide a clear, concise, and detailed explanation of the endpoint’s business logic, including the request flow, middleware involvement, and final response handling."
   },
   "query_params": {
     "type": "array",
     "description": "An array of objects documenting each query parameter.",
     "items": {
       "type": "object",
       "properties": {
         "name": {"type": "string"},
         "description": {"type": "string", "description": "Brief description of the parameter's purpose."},
         "type": {"type": "string", "enum": ["string", "integer", "number", "boolean", "array", "object"]}
       },
       "required": ["name", "description", "type"]
     }
   }
,
   "request_body": {
     "type": "object",
     "description": "An object describing the request body, if any.",
     "properties": {
       "description": {"type": "string", "description": "A high-level description of the request body's purpose."},
       "schema": {
         "type": "object",
         "description": "A JSON schema representation of the request body payload."
       }
     },
     "required": ["description", "schema"]
   }
 },
 "required": ["logic_explanation", "query_params", "request_body"]
}
```

Example Output:
```json
{
 "logic_explanation": "The endpoint retrieves a user's profile by their unique ID. It first validates the 'id' path parameter, then queries the database for the user record. If the user is not found, it returns a 404 error. Otherwise, it returns the user's data.",
 "query_params": [
   {
     "name": "include_email",
     "description": "Specifies whether to include the user's email address in the response.",
     "type": "boolean"
   }
 ],
 "request_body": {
   "description": "None.",
   "schema": {}
 }
}
```
"""

REQUIRED_KEYS = {"logic_explanation", "query_params", "request_body"}

def validate_response(api_details: dict) -> dict:
    """Ensure AI response matches expected schema with safe defaults."""
    if not isinstance(api_details, dict):
        return {
            "logic_explanation": "_Invalid AI response type._",
            "query_params": [],
            "request_body": {"description": "None.", "schema": {}},
        }

    validated = {}
    validated["logic_explanation"] = api_details.get("logic_explanation", "")

    query_params = api_details.get("query_params", [])
    if isinstance(query_params, list):
        validated_params = []
        for param in query_params:
            if isinstance(param, dict) and "name" in param and "description" in param and "type" in param:
                validated_params.append(param)
        validated["query_params"] = validated_params
    else:
        validated["query_params"] = []

    request_body = api_details.get("request_body", {})
    if isinstance(request_body, dict):
        validated["request_body"] = {
            "description": request_body.get("description", "None."),
            "schema": request_body.get("schema", {}),
        }
    else:
        validated["request_body"] = {"description": "None.", "schema": {}}

    return validated

def enhance_with_ollama(endpoints: List[Dict], model: str = "llama3:instruct") -> List[Dict]:
    """Enhances each endpoint with an AI-generated explanation using the Ollama REST API."""
    for i, endpoint in enumerate(endpoints):
        source = endpoint.get("source")
        meta = f"[{endpoint.get('method','?')}] {endpoint.get('path','?')}"
        print(f"\n🔍 Analyzing {meta}... ({i+1}/{len(endpoints)})")

        if not source:
            endpoint["ai_details"] = {
                "logic_explanation": "_No source code found._",
                "query_params": [],
                "request_body": {"description": "None.", "schema": {}},
            }
            continue

        user_prompt = f"""
Analyze the following API endpoint code to generate documentation based on the schema provided in your system prompt.

Endpoint Source Code:
{source}
"""

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
                    outer_json = json.loads(response_text)
                    api_details_str = outer_json.get("response", "{}")
                    api_details = json.loads(api_details_str)
                    endpoint["ai_details"] = validate_response(api_details)
                else:
                    raise RuntimeError(f"API request failed with status {response.status}: {response.read().decode('utf-8')}")

        except Exception as e:
            print(f"❌ Error analyzing {meta}: {e}")
            endpoint["ai_details"] = {
                "logic_explanation": f"_Ollama analysis failed: {e}_",
                "query_params": [],
                "request_body": {"description": "None.", "schema": {}},
            }
            if isinstance(e, (urllib.error.URLError, ConnectionRefusedError)):
                print("   Could not connect to Ollama. Aborting analysis.")
                return endpoints

    print("\n✅ AI analysis complete.")
    return endpoints
