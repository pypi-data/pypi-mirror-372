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

    def think(self, question: str, max_steps: int = 5, return_thoughts: bool = False) -> Union[str, tuple]:
        """
        Iteratively reason and search to answer a question, showing the agent's thought process.
        Args:
            question (str): The user query.
            max_steps (int): Maximum reasoning steps.
            return_thoughts (bool): If True, return (answer, thoughts) tuple.
        Returns:
            str or (str, list): Final answer, or (answer, thought trace) if return_thoughts is True.
        """
        thoughts = []
        context = self._messages(question)
        current_query = question
        answer = None
        for step in range(max_steps):
            # 1. Ask the model: "What should I think/do next?"
            thought_prompt = (
                f"You are an AI agent. Here is the current question: '{question}'.\n"
                f"Here is the context so far: {context}\n"
                "What is your next thought or action? "
                "If you are ready to answer, say 'FINAL ANSWER: ...'"
            )
            msgs = context + [{"role": "user", "content": thought_prompt}]
            thought = self.model.send(msgs)
            thoughts.append(thought)
            # 2. Check if model is ready to answer
            if thought.strip().lower().startswith("final answer:"):
                answer = thought.split(":", 1)[1].strip()
                break
            # 3. Optionally: search memory/tools (not implemented, placeholder)
            # For now, just append the thought to context and continue
            context.append({"role": "assistant", "content": thought})
        else:
            # If loop ends without FINAL ANSWER
            answer = "No final answer produced after reasoning steps."
        if return_thoughts:
            return answer, thoughts
        return answer