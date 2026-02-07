from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.0-flash"  # Using the latest stable Gemini model


def query_llm(prompt: str) -> str:
    """Query the Gemini API with the given prompt."""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        return response.text
    except Exception as e:
        raise RuntimeError(f"Error querying Gemini API: {str(e)}")
