# api.py
# Handles interactions with the Ollama REST API, including streaming support

import requests
import json

def api(prompt, model="tinyllama", base_url="http://localhost:11434", stream=False):
    """Send a prompt to the Ollama API and return the response or stream."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        response = requests.post(f"{base_url}/api/generate", json=payload, stream=stream)
        response.raise_for_status()

        if stream:
            def generate():
                for line in response.iter_lines():
                    if line:
                        yield json.loads(line.decode('utf-8')).get("response", "")
            return generate()
        else:
            return response.json().get("response", "No response received")
    except requests.RequestException as e:
        return f"Error: Could not connect to Ollama. Is it running? ({str(e)})"
