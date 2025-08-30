from __future__ import annotations
import json
import os
from typing import Dict, List
from pathlib import Path
from openai import OpenAI

# -------- CONFIGURATION --------
API_FILE = Path.home() / ".openai_api_key"
DEFAULT_MODEL = "gpt-4o-mini"

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
    },
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

# -------- API KEY HANDLING --------
def get_api_key() -> str:
    """Retrieve stored OpenAI API key, ask if missing."""
    if API_FILE.exists():
        return API_FILE.read_text().strip()
    else:
        api_key = input("Enter your OpenAI API Key: ").strip()
        API_FILE.write_text(api_key)
        return api_key

def update_api_key(new_key: str) -> None:
    """Update stored API key."""
    API_FILE.write_text(new_key.strip())
    print("✅ API key updated successfully.")

# -------- VALIDATION --------
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
    validated["query_params"] = api_details.get("query_params", [])
    validated["request_body"] = api_details.get(
        "request_body", {"description": "None.", "schema": {}}
    )

    # enforce schema shape
    if not isinstance(validated["query_params"], list):
        validated["query_params"] = []
    if not isinstance(validated["request_body"], dict):
        validated["request_body"] = {"description": "None.", "schema": {}}

    return validated

# -------- MAIN FUNCTION --------
def enhance_with_openai(endpoints: List[Dict], model: str = DEFAULT_MODEL) -> List[Dict]:
    """Enhances each endpoint with an AI-generated explanation using OpenAI API."""
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)

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

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            raw = response.choices[0].message.content.strip()
            api_details = json.loads(raw)
            endpoint["ai_details"] = validate_response(api_details)

        except Exception as e:
            print(f"❌ Error analyzing {meta}: {e}")
            endpoint["ai_details"] = {
                "logic_explanation": f"_OpenAI analysis failed: {e}_",
                "query_params": [],
                "request_body": {"description": "None.", "schema": {}},
            }

    print("\n✅ AI analysis complete.")
    return endpoints

