import requests
from typing import Optional

# Simple Ollama client that talks to a local Ollama HTTP API (default port 11434).
# Model used as a fallback: phi3-fast:latest

OLLY_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "phi3-fast:latest"


def query_ollama(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 30) -> str:
    """Query a local Ollama server. Returns text output on success or raises RuntimeError.

    Note: Ollama typically streams responses; this implementation requests synchronously
    and returns whatever text the server provides. Ensure Ollama is running locally.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(OLLY_URL, json=payload, timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Error connecting to Ollama server: {e}")

    if resp.status_code != 200:
        # include body for easier debugging
        raise RuntimeError(f"Ollama error {resp.status_code}: {resp.text}")

    # Try to parse JSON responses first
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            data = resp.json()
        except Exception:
            return resp.text

        # Common sensible fallbacks for returned fields
        if isinstance(data, dict):
            for key in ("text", "content", "output", "result"):
                if key in data and isinstance(data[key], (str, list)):
                    val = data[key]
                    if isinstance(val, list):
                        return "".join(map(str, val))
                    return str(val)

            # some Ollama endpoints stream chunks under 'choices' or similar
            if "choices" in data and isinstance(data["choices"], list):
                parts = []
                for c in data["choices"]:
                    if isinstance(c, dict):
                        parts.append(c.get("text") or c.get("message") or "")
                    else:
                        parts.append(str(c))
                return "".join(parts)

        return resp.text

    # Fallback: return raw text
    return resp.text
