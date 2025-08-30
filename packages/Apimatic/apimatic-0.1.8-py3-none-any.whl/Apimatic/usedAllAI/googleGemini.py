from __future__ import annotations
import json
import os
from typing import Dict, List
from pathlib import Path
import google.generativeai as genai
import google.ai.generativelanguage as glm
import re

API_FILE = Path.home() / ".gemini_api_key"
DEFAULT_MODEL = "gemini-1.5-flash"

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

def get_api_key() -> str:
    if API_FILE.exists():
        return API_FILE.read_text().strip()
    else:
        api_key = input("Enter your Gemini API Key: ").strip()
        API_FILE.write_text(api_key)
        return api_key

def update_api_key(new_key: str) -> None:
    API_FILE.write_text(new_key.strip())
    print("✅ API key updated successfully.")

REQUIRED_KEYS = {"logic_explanation", "query_params", "request_body"}

def validate_response(api_details: dict) -> dict:
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

def enhance_with_gemini(endpoints: List[Dict], model_name: str = DEFAULT_MODEL) -> List[Dict]:
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Gemini API key not found. Please set it using 'apimatic config --set-gemini-key YOUR_KEY'")

    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)

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
            response = model.generate_content(
                user_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0,
                )
            )
            
            raw = response.text.strip()
            
            # Remove potential markdown code block wrappers
            if raw.startswith("```json"):
                raw = raw.strip("`").strip("json").strip()
            
            # Use regex to find and extract the JSON object
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                raw = match.group(0)
            
            # Clean up potential trailing commas before parsing
            cleaned_raw = re.sub(r',(\s*[\}\]])', r'\1', raw)

            api_details = json.loads(cleaned_raw)
            endpoint["ai_details"] = validate_response(api_details)

        except Exception as e:
            print(f"❌ Error analyzing {meta}: {e}")
            endpoint["ai_details"] = {
                "logic_explanation": f"_Gemini analysis failed: {e}_",
                "query_params": [],
                "request_body": {"description": "None.", "schema": {}},
            }

    print("\n✅ AI analysis complete.")
    return endpoints
