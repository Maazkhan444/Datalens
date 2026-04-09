import json
import re
from google import genai

class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.selected_model_name = "gemini-2.5-flash"

    def analyze(self, user_query, dataset_metadata):
        # UPDATED PERSONA PROMPT
        prompt = f"""
        Act as DataGuru, the intelligent AI assistant for the DataLens platform.
        You are friendly, professional, and concise.
        
        DATA CONTEXT:
        {json.dumps(dataset_metadata)}
        
        USER QUERY:
        {user_query}
        
        INSTRUCTIONS:
        1. Reply in valid JSON only.
        2. "response": Your spoken answer to the user.
        3. "visualization": null or {{ "chart_type": "...", "x": "...", "y": "..." }}
        
        JSON SCHEMA:
        {{
            "response": "string",
            "visualization": null,
            "actions": []
        }}
        """
        
        try:
            result = self.client.models.generate_content(
                model=self.selected_model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            text = result.text.strip()
            if "```" in text:
                match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
                if match: text = match.group(1).strip()
            return json.loads(text)
        except Exception as e:
            print(f"DEBUG - Gemini API Error: {str(e)}")
            return {"response": f"DataGuru Error: {str(e)}", "visualization": None}
