from typing import List, Dict, Optional, Union
from .models.openai_adapter import OpenAIAdapter, ModelAdapterBase
from .memory.sqlite import SQLiteMemory

# Default system prompt for the agent
DEFAULT_SYSTEM = {"role": "system", "content": "You are a helpful assistant."}

class Noctis:
    """
    Main class for creating AI agents.

    Example (one-liner):
        from noctis import Noctis
        agent = Noctis("gpt-4o-mini")
        print(agent.ask("Hello world"))
    """

    def __init__(
        self,
        model: Union[str, ModelAdapterBase] = "gpt-4o-mini",
        *,
        memory: Optional[Union[str, SQLiteMemory]] = None,
        tools: Optional[list] = None,
    ):
        # Model setup: string → OpenAIAdapter, or use a custom adapter
        self.model = model if isinstance(model, ModelAdapterBase) else OpenAIAdapter(model)
        # Memory setup: string path → SQLiteMemory, or custom memory object
        self.memory = memory if isinstance(memory, SQLiteMemory) else SQLiteMemory(memory)
        # Tools: currently using global registry; can extend per-agent later
        self.tools = tools or []

    def _messages(self, user_text: str) -> List[Dict[str, str]]:
        """
        Build the message list to send to the model:
        1. System prompt
        2. Recent memory (last 10 messages)
        3. Current user input
        """
        msgs = [DEFAULT_SYSTEM]
        msgs.extend(self.memory.get_recent(10))
        msgs.append({"role": "user", "content": user_text})
        return msgs

    def ask(self, text: str) -> str:
        """
        Send a prompt to the agent and get a response.
        Automatically stores both user input and assistant response in memory.
        """
        msgs = self._messages(text)
        reply = self.model.send(msgs)
        self.memory.append("user", text)
        self.memory.append("assistant", reply)
        return reply

    # Alias for ask(), more natural for chat
    chat = ask
