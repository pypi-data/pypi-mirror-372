from dataclasses import dataclass
from typing import Callable, Dict, Optional
from jsonschema import validate, ValidationError
import requests
from bs4 import BeautifulSoup

# ----------------------------
# Tool Framework
# ----------------------------

@dataclass
class ToolSpec:
    """
    Stores metadata for a tool:
    - name: unique tool name
    - func: the Python function to call
    - schema: optional JSON schema for input validation
    - description: optional human-readable description
    """
    name: str
    func: Callable
    schema: Optional[Dict] = None
    description: Optional[str] = None


# Global registry of tools
_REGISTRY: Dict[str, ToolSpec] = {}


def tool(name: str, schema: Optional[Dict] = None, description: Optional[str] = None):
    """
    Decorator to register a Python function as a tool.

    Example:
        @tool("math.add", {"type":"object","properties":{"a":{"type":"number"},"b":{"type":"number"}}, "required":["a","b"]})
        def add(a, b):
            return a + b
    """
    def decorator(fn: Callable):
        _REGISTRY[name] = ToolSpec(name=name, func=fn, schema=schema, description=description)
        return fn
    return decorator


def get_registry() -> Dict[str, ToolSpec]:
    """Returns all registered tools."""
    return _REGISTRY


def run_tool(name: str, payload: Dict):
    """
    Run a registered tool with input validation.

    Args:
        name: tool name
        payload: dictionary of inputs

    Raises:
        RuntimeError: if tool doesn't exist or input is invalid
    """
    spec = _REGISTRY.get(name)
    if not spec:
        raise RuntimeError(f"Unknown tool: {name}")
    if spec.schema:
        try:
            validate(payload, spec.schema)
        except ValidationError as e:
            raise RuntimeError(f"Tool '{name}' payload invalid: {e.message}")
    return spec.func(**payload)


# ----------------------------
# Example Tool: web_fetch
# ----------------------------

@tool(
    name="web.fetch",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"}
        },
        "required": ["url"]
    },
    description="Fetches and cleans the text content of a given URL"
)
def web_fetch(url: str) -> str:
    """
    Fetches the text content from a given URL.

    Args:
        url (str): The full URL (e.g., 'https://www.example.com') to fetch.

    Returns:
        str: The cleaned text content of the page, or an error message.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove scripts and styles
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Extract and clean text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text or f"Error: No text content found at {url}"

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"