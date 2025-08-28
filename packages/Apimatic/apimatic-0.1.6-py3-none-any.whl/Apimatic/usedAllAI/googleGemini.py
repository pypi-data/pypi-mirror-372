from __future__ import annotations
import json
import os
from typing import Dict, List
from pathlib import Path
import google.generativeai as genai
import google.ai.generativelanguage as glm # for the API response objects

API_FILE = Path.home() / ".gemini_api_key"
DEFAULT_MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """
You are an expert software engineer and senior technical writer. Your task is to analyze the source code for a single API endpoint and generate a documentation object in JSON format.

### STRICT RULES (VERY IMPORTANT)

1.  **Analyze, Don't Speculate:** Base your output *only* on the provided source code. Do not invent or assume functionality that isn't explicitly present.
2.  **Accurate Parameter Detection:**
    *   **Path Parameters:** Identify variables embedded in the URL path (e.g., `/users/{user_id}`).
    *   **Query Parameters:** Identify parameters read from the URL query string (e.g., `request.args` in Flask, or FastAPI function arguments that are not part of the path).
    *   **Request Body:** Identify data read from the request body (e.g., from a Pydantic model or `request.json`).
3.  **JSON Output Only:** Return *only* a single, valid JSON object. Do not include any other text, markdown, or explanations outside of the JSON structure.
4.  **Field Correctness:**
    *   If there are no query parameters, the `query_params` field must be an empty array (`[]`).
    *   If there is no request body, the `request_body` field must be `{"description": "None.", "schema": {}}`.

### OUTPUT STRUCTURE

Your JSON output must have the following keys:

1.  `"logic_explanation"`: **(High-Quality Explanation)**
    *   Provide a concise, step-by-step summary of the endpoint's business logic.
    *   Focus on the **"how" and "why"**: What is the endpoint's purpose? How does it achieve it?
    *   Explain the data flow: Where does data come from (e.g., database, external API)? How is it processed or transformed?
    *   Mention any key validation, error handling, or security measures.
    *   Write in clear, active voice. Aim for 4-6 impactful sentences.

2.  `"query_params"`: An array of objects, where each object represents a query parameter and has the keys: `name`, `type`, and `description`.

3.  `"request_body"`: An object describing the JSON request body, containing the keys: `description` and `schema`.

### FINAL REQUIREMENT

- Return ONLY a single valid JSON object with the keys: `"logic_explanation"`, `"query_params"`, and `"request_body"`.
"""

# -------- API KEY HANDLING --------
def get_api_key() -> str:
    """Retrieve stored Gemini API key, ask if missing."""
    if API_FILE.exists():
        return API_FILE.read_text().strip()
    else:
        api_key = input("Enter your Gemini API Key: ").strip()
        API_FILE.write_text(api_key)
        return api_key

def update_api_key(new_key: str) -> None:
    """Update stored API key."""
    API_FILE.write_text(new_key.strip())
    print("✅ API key updated successfully.")

# -------- MAIN FUNCTION --------
def enhance_with_gemini(endpoints: List[Dict], model_name: str = DEFAULT_MODEL) -> List[Dict]:
    """Enhances each endpoint with an AI-generated explanation using Gemini API."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Gemini API key not found. Please set it using 'apimatic config --set-gemini-key YOUR_KEY'")

    genai.configure(api_key=api_key)
   
    model = genai.GenerativeModel(model_name)

    for i, endpoint in enumerate(endpoints):
        source = endpoint.get("source")
        if not source:
            endpoint["ai_details"] = {
                "logic_explanation": "_No source code found to generate a description._",
                "query_params": [],
                "request_body": {},
            }
            continue

        print(f"🔍 Analyzing {endpoint.get('summary', 'endpoint')}... ({i+1}/{len(endpoints)})")

        user_prompt = f"{SYSTEM_PROMPT}\n\nHere is the API endpoint source code:\n\n{source}"

        try:
            response = model.generate_content(
                user_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0,
                )
            )

            api_details = json.loads(response.text)

            endpoint["ai_details"] = {
                "logic_explanation": api_details.get("logic_explanation", ""),
                "query_params": api_details.get("query_params", []),
                "request_body": api_details.get("request_body", {}),
            }

        except Exception as e:
            print(f"❌ Error analyzing {endpoint.get('summary')}: {e}")
            endpoint["ai_details"] = {
                "logic_explanation": f"_Gemini analysis failed: {e}_",
                "query_params": [],
                "request_body": {},
            }
            continue

    print("✅ AI analysis complete.")
    return endpoints