import google.generativeai as genai
import json
import re

class GeminiClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        
        # Priority Logic
        priority_list = [
            "models/gemini-1.5-flash", 
            "models/gemini-flash-latest", 
            "models/gemini-pro"
        ]
        self.selected_model_name = "models/gemini-pro"
        try:
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            for p in priority_list:
                if p in available:
                    self.selected_model_name = p
                    break
        except: pass

        self.model = genai.GenerativeModel(self.selected_model_name)

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
            result = self.model.generate_content(prompt)
            text = result.text.strip()
            if "```" in text:
                match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
                if match: text = match.group(1).strip()
            return json.loads(text)
        except Exception as e:
            return {"response": f"DataGuru Error: {str(e)}", "visualization": None}
