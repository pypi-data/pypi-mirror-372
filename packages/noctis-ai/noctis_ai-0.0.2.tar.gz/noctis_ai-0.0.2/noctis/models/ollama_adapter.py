import requests
import json

class OllamaAdapter:
    def __init__(self, base_url="http://localhost:11434", model="llama2"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, messages, model: str = None):
        """
        Send a list of messages to the Ollama API and return the full response.
        """
        chosen_model = model or self.model
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": chosen_model,
            "messages": messages
        }

        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        full_reply = ""
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            if "message" in data and "content" in data["message"]:
                full_reply += data["message"]["content"]
            if data.get("done", False):
                break

        return full_reply.strip()

    def generate(self, prompt, model: str = None):
        """
        Generate text from a prompt using Ollama's /api/generate endpoint.
        """
        chosen_model = model or self.model
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": chosen_model,
            "prompt": prompt
        }

        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        full_reply = ""
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                full_reply += data["response"]
            if data.get("done", False):
                break

        return full_reply.strip()
