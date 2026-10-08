import json
import os
import subprocess
from typing import Callable, Dict, Any, List
from ddgs import DDGS
import config
from core.repl_sandbox import SecureREPL

TOOLS_REGISTRY: Dict[str, Callable] = {}
TOOL_SCHEMAS: List[Dict[str, Any]] = []
REPL = SecureREPL()

def register_tool(name: str, description: str, parameters: dict):
    def decorator(func: Callable):
        func._tool_metadata = {"name": name, "description": description, "parameters": parameters}
        TOOLS_REGISTRY[name] = func
        TOOL_SCHEMAS[:] = [s for s in TOOL_SCHEMAS if s["function"]["name"] != name]
        TOOL_SCHEMAS.append({"type": "function", "function": func._tool_metadata})
        return func
    return decorator

def is_path_safe(filepath: str) -> bool:
    if not config.STRICT_SANDBOX_MODE:
        return True
    abs_target = os.path.realpath(filepath)
    abs_workspace = os.path.realpath(config.WORKSPACE_DIR)
    return abs_target.startswith(abs_workspace)

@register_tool(
    name="python_repl",
    description="Executes python code in a persistent stateful REPL environment.",
    parameters={
        "type": "object",
        "properties": {"code": {"type": "string"}},
        "required": ["code"]
    }
)
def python_repl(code: str) -> str:
    return REPL.execute(code)

@register_tool(
    name="run_terminal",
    description="Executes a system shell command safely.",
    parameters={
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"]
    }
)
def run_terminal(command: str) -> str:
    for blocked in config.BLOCKED_COMMANDS:
        if blocked in command:
            return f"SECURITY REFUSAL: Command contains blocked dangerous syntax: '{blocked}'."
    try:
        res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=config.WORKSPACE_DIR)
        return res.stdout or res.stderr or "Command executed successfully."
    except Exception as e:
        return f"Execution error: {str(e)}"

@register_tool(
    name="read_file",
    description="Reads file contents inside the safe workspace.",
    parameters={
        "type": "object",
        "properties": {"filepath": {"type": "string"}},
        "required": ["filepath"]
    }
)
def read_file(filepath: str) -> str:
    target_path = os.path.join(config.WORKSPACE_DIR, filepath) if not os.path.isabs(filepath) else filepath
    if not is_path_safe(target_path):
        return f"SECURITY REFUSAL: Path '{filepath}' violates workspace boundary."
    if not os.path.exists(target_path):
        return f"File '{filepath}' not found."
    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()

@register_tool(
    name="write_file",
    description="Writes content to a file path inside the workspace.",
    parameters={
        "type": "object",
        "properties": {
            "filepath": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["filepath", "content"]
    }
)
def write_file(filepath: str, content: str) -> str:
    target_path = os.path.join(config.WORKSPACE_DIR, filepath) if not os.path.isabs(filepath) else filepath
    if not is_path_safe(target_path):
        return f"SECURITY REFUSAL: Path '{filepath}' violates workspace boundary."
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully wrote to '{filepath}'."

@register_tool(
    name="web_search",
    description="Performs live search query on DuckDuckGo and returns article title, body, and URL snippets.",
    parameters={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
)
def web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found."
            snippets = []
            for r in results:
                title = r.get("title", "No Title")
                body = r.get("body", "No description")
                url = r.get("href", "")
                snippets.append(f"Title: {title}\nSnippet: {body}\nURL: {url}")
            return "\n---\n".join(snippets)
    except Exception as e:
        return f"Search error: {str(e)}"
