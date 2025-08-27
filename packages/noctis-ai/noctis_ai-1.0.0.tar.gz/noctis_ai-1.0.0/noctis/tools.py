from dataclasses import dataclass
from typing import Callable, Dict, Optional, List, Any
from jsonschema import validate, ValidationError, FormatChecker
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from urllib.parse import urljoin, urlparse

# ----------------------------
# Tool Framework
# ----------------------------

@dataclass
class ToolSpec:
    name: str
    func: Callable
    schema: Optional[Dict] = None
    description: Optional[str] = None

_REGISTRY: Dict[str, ToolSpec] = {}

def tool(name: str, schema: Optional[Dict] = None, description: Optional[str] = None):
    def decorator(fn: Callable):
        _REGISTRY[name] = ToolSpec(name=name, func=fn, schema=schema, description=description)
        return fn
    return decorator

def get_registry() -> Dict[str, ToolSpec]:
    return _REGISTRY

def run_tool(name: str, payload: Dict):
    spec = _REGISTRY.get(name)
    if not spec:
        raise RuntimeError(f"Unknown tool: {name}")
    if spec.schema:
        try:
            validate(payload, spec.schema, format_checker=FormatChecker())
        except ValidationError as e:
            raise RuntimeError(f"Tool '{name}' payload invalid: {e.message}")
    return spec.func(**payload)

# ----------------------------
# Internal Helpers
# ----------------------------

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

def _make_session(user_agent: str = DEFAULT_USER_AGENT) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent})
    return s

def _clean_text_from_soup(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return "\n".join(chunk for chunk in chunks if chunk)

def _safe_absolute_url(base: str, link: str) -> Optional[str]:
    if not link:
        return None
    parsed = urlparse(link)
    if parsed.scheme and parsed.netloc:
        return link
    try:
        return urljoin(base, link)
    except Exception:
        return None

def _fetch_url_content(url: str, session: requests.Session, timeout: int = 10, snippet_chars: int = 300) -> dict:
    result = {"url": url, "status_code": None, "title": None, "text": None, "error": None}
    try:
        resp = session.get(url, timeout=timeout)
        result["status_code"] = resp.status_code
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        title_tag = soup.find("title")
        result["title"] = title_tag.get_text().strip() if title_tag else None
        text = _clean_text_from_soup(soup)
        if snippet_chars and len(text) > snippet_chars:
            result["text"] = text[:snippet_chars]
        else:
            result["text"] = text
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"parsing error: {e}"
    return result

# ----------------------------
# Web Search Helpers
# ----------------------------

@lru_cache(maxsize=256)
def _search_duckduckgo_html(query: str, num_results: int = 5, user_agent: str = DEFAULT_USER_AGENT) -> List[Dict[str, Any]]:
    url = "https://duckduckgo.com/html/"
    session = _make_session(user_agent)
    try:
        resp = session.post(url, data={"q": query}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        anchors = soup.select("a.result__a") or soup.select("a[href^='http']")
        seen = set()
        for a in anchors:
            href = a.get("href")
            if not href:
                continue
            target = href
            title = a.get_text(strip=True)
            abs_url = _safe_absolute_url(url, target)
            if not abs_url or abs_url in seen:
                continue
            seen.add(abs_url)
            snippet_tag = a.find_next("a").find_next(string=True) if a.find_next("a") else None
            snippet = snippet_tag.strip() if snippet_tag and isinstance(snippet_tag, str) else ""
            results.append({"title": title, "url": abs_url, "snippet": snippet})
            if len(results) >= num_results:
                break
        return results
    except Exception:
        return []

def _search_bing(query: str, num_results: int = 5, user_agent: str = DEFAULT_USER_AGENT) -> List[Dict[str, Any]]:
    url = "https://www.bing.com/search"
    session = _make_session(user_agent)
    try:
        resp = session.get(url, params={"q": query}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        seen = set()
        for li in soup.select("li.b_algo")[: num_results * 3]:
            a = li.find("h2").find("a") if li.find("h2") else None
            if not a:
                continue
            href = a.get("href")
            if not href:
                continue
            abs_url = _safe_absolute_url(url, href)
            if not abs_url or abs_url in seen:
                continue
            seen.add(abs_url)
            title = a.get_text(strip=True)
            snippet_tag = li.select_one(".b_caption p")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            results.append({"title": title, "url": abs_url, "snippet": snippet})
            if len(results) >= num_results:
                break
        return results
    except Exception:
        return []

# ----------------------------
# Registered Tools
# ----------------------------

@tool(
    name="web.search",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_results": {"type": "integer", "minimum": 1, "maximum": 20},
            "provider": {"type": "string", "enum": ["ddg", "bing"]},
        },
        "required": ["query"]
    },
    description="Search the web and return a list of results (title, url, snippet). Providers: ddg, bing"
)
def web_search(
    query: str,
    num_results: int = 5,
    provider: str = "ddg"
) -> List[Dict[str, Any]]:
    num_results = max(1, min(num_results, 20))
    results = []
    if provider == "ddg":
        results = _search_duckduckgo_html(query, num_results)
        if not results:
            results = _search_bing(query, num_results)
    else:
        results = _search_bing(query, num_results)
        if not results:
            results = _search_duckduckgo_html(query, num_results)
    normalized = []
    for r in results[:num_results]:
        normalized.append({
            "title": r.get("title") or "",
            "url": r.get("url") or "",
            "snippet": r.get("snippet") or ""
        })
    return normalized

@tool(
    name="web.fetch",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "timeout": {"type": "integer", "minimum": 1},
            "snippet_chars": {"type": "integer", "minimum": 0}
        },
        "required": ["url"]
    },
    description="Fetch and clean a single URL, returning title/text/status/error"
)
def web_fetch(
    url: str,
    timeout: int = 10,
    snippet_chars: int = 300
) -> Dict[str, Any]:
    session = _make_session()
    return _fetch_url_content(url=url, session=session, timeout=timeout, snippet_chars=snippet_chars)

@tool(
    name="web.fetch_many",
    schema={
        "type": "object",
        "properties": {
            "urls": {"type": "array", "items": {"type": "string", "format": "uri"}},
            "timeout": {"type": "integer", "minimum": 1},
            "snippet_chars": {"type": "integer", "minimum": 0},
            "max_workers": {"type": "integer", "minimum": 1}
        },
        "required": ["urls"]
    },
    description="Fetch multiple URLs in parallel. Returns a mapping url -> {title,text,status_code,error}"
)
def web_fetch_many(
    urls: List[str],
    timeout: int = 10,
    snippet_chars: int = 300,
    max_workers: int = 3
) -> Dict[str, Dict[str, Any]]:
    session = _make_session()
    results: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_fetch_url_content, url, session, timeout, snippet_chars): url for url in urls}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                results[url] = fut.result()
            except Exception as e:
                results[url] = {"url": url, "status_code": None, "title": None, "text": None, "error": str(e)}
    return results

@tool(
    name="web.search_fetch",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_results": {"type": "integer", "minimum": 1, "maximum": 10},
            "provider": {"type": "string", "enum": ["ddg", "bing"]},
            "snippet_chars": {"type": "integer", "minimum": 0},
            "max_paragraphs": {"type": "integer", "minimum": 1},
            "max_workers": {"type": "integer", "minimum": 1}
        },
        "required": ["query"]
    },
    description="Search the web and fetch structured content from top URLs automatically."
)
def web_search_fetch(
    query: str,
    num_results: int = 3,
    provider: str = "ddg",
    snippet_chars: int = 300,
    max_paragraphs: int = 5,
    max_workers: int = 3
) -> List[Dict[str, Any]]:
    # Step 1: Search
    search_results = run_tool("web.search", {"query": query, "num_results": num_results, "provider": provider})
    urls = [r["url"] for r in search_results]

    # Step 2: Fetch content
    fetched = run_tool("web.fetch_many", {"urls": urls, "snippet_chars": snippet_chars, "max_workers": max_workers})

    # Step 3: Combine
    combined_results = []
    for r in search_results:
        url = r["url"]
        content = fetched.get(url, {})
        paragraphs = content.get("text", "").split("\n")[:max_paragraphs] if content.get("text") else []
        combined_results.append({
            "title": r.get("title") or content.get("title") or "",
            "url": url,
            "snippet": r.get("snippet") or "",
            "paragraphs": paragraphs,
            "status_code": content.get("status_code"),
            "error": content.get("error")
        })
    return combined_results
@tool(
    name="agent.run",
    schema={
        "type": "object",
        "properties": {
            "agent": {"type": "object"},
            "query": {"type": "string"}
        },
        "required": ["agent"]
    },
    description="Execute actions for the agent based on its goal and allowed tools."
)
def agent_run(agent: Dict[str, Any], query: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes simple actions based on the agent's goal and allowed tools.
    Currently supports `web.search` and `web.fetch`.
    Stores results in agent's memory.
    """
    memory = agent.get("memory", {})
    results = []

    # Use web.search if allowed
    if "web.search" in agent.get("tools", []) and query:
        results = run_tool("web.search", {"query": query, "num_results": 3, "provider": "ddg"})
        memory["last_search_results"] = results

    # Use web.fetch if allowed
    if "web.fetch" in agent.get("tools", []) and memory.get("last_search_results"):
        urls = [r["url"] for r in memory["last_search_results"]]
        fetched = run_tool("web.fetch_many", {"urls": urls, "snippet_chars": 300, "max_workers": 3})
        memory["last_fetched_results"] = fetched

    agent["memory"] = memory
    return {"agent": agent, "results": results, "fetched": memory.get("last_fetched_results")}
@tool(
    name="agent.create",
    schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "goal": {"type": "string"},
            "constraints": {"type": "array", "items": {"type": "string"}},
            "tools": {"type": "array", "items": {"type": "string"}},
            "memory": {"type": "object"}
        },
        "required": ["name", "goal"]
    },
    description="Create a new AI agent by specifying its name, goal, optional constraints, a whitelist of tools, and memory."
)
def agent_create(
    name: str,
    goal: str,
    constraints: Optional[List[str]] = None,
    tools: Optional[List[str]] = None,
    memory: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        "name": name,
        "goal": goal,
        "constraints": constraints if constraints else [],
        "tools": tools if tools else [],
        "memory": memory if memory else {}
    }