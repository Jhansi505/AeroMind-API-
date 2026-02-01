import requests
import json

# Local Ollama configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma:latest"  # Can also try: gemma:7b, gemma:2b, llama3:latest


def query_llm(prompt: str) -> str:
    """Query the local Gemini model via Ollama API."""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        raise RuntimeError(f"Error querying local Gemini model: {str(e)}")
