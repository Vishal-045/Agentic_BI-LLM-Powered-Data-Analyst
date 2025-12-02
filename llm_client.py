import os
# We still import OpenAI, but we will configure it to point to the Gemini API endpoint
from openai import OpenAI 
# You may want to keep this in case you switch to the native client later:
# from google import genai 

class LLMClient:
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = None # Default OpenAI endpoint
        elif self.provider == "gemini":
            # 1. Get the Gemini API Key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY not set")
            
            # 2. Set the Base URL to Google's OpenAI-compatible endpoint
            # This is the key to using the existing 'openai' library with Gemini!
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        else:
            raise RuntimeError(f"Unknown LLM Provider: {self.provider}")
        
        # Initialize the OpenAI client with the correct key and base URL
        # The 'openai' library is being used as a client for the Gemini API
        self._client = OpenAI(api_key=api_key, base_url=base_url)


    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        # Use the configured model name from the environment variables
        if self.provider == "openai":
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "gemini":
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash") # Use a Gemini model name
        else:
            return f"[LLM Placeholder] {prompt[:200]}"
            
        response = self._client.chat.completions.create(
            # Use the model name specific to the current provider
            model=model_name, 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()