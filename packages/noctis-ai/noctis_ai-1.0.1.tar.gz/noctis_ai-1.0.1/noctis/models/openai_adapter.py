# noctis/models/openai_adapter.py
from abc import ABC, abstractmethod
from typing import List, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv


# Load .env file (once, globally)
load_dotenv()


# ---- Base Class ----
class ModelAdapterBase(ABC):
    @abstractmethod
    def send(self, messages: List[Dict[str, str]]) -> str:
        """Send chat messages to the model and return response text."""
        pass


# ---- Mock Adapter (for testing) ----
class MockAdapter(ModelAdapterBase):
    def __init__(self, model: str = "mock-model"):
        self.model = model

    def send(self, messages: List[Dict[str, str]]) -> str:
        last_msg = messages[-1]["content"] if messages else ""
        return f"[Mock:{self.model}] You said: {last_msg}"


# ---- Real OpenAI Adapter ----
class OpenAIAdapter(ModelAdapterBase):
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = None):
        self.model = model
        # Prefer explicit api_key, otherwise fallback to env
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY in .env")
        self.client = OpenAI(api_key=api_key)

    def send(self, messages: List[Dict[str, str]], model: str = None) -> str:
        """Send chat messages to OpenAI API and return assistant reply.
        Use provided model if given, otherwise use self.model.
        """
        chosen_model = model or self.model
        response = self.client.chat.completions.create(
            model=chosen_model,
            messages=messages
        )
        return response.choices[0].message.content