import requests
import json

from memory.store import get_all_memory

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:4b"

SYSTEM_PROMPT = """
You are JARVIS, an autonomous AI assistant running locally on a Mac.

PERSONALITY:
- Calm, intelligent, confident and concise.
- British-style professional manner.
- Occasionally address the user as "sir".
- Natural conversational tone.
- Never ramble.
- Never ask unnecessary follow-up questions.
- Never say "Is there anything else I can assist you with?"

MEMORY:
You have access to persistent memory about the user.
Use the supplied memory naturally when relevant.
Do not claim to remember something that is not in memory.
If the user tells you something worth remembering, the agent may store it separately.

TOOLS:
open_app(app_name)
close_app(app_name)
list_open_apps()
open_website(url)
open_url_in_safari(url)
search_web(query)
system_status()

TOOL RULES:
When the user requests an action that requires a tool, output ONLY:

TOOL: tool_name
ARGS: {"argument": "value"}

Examples:

TOOL: open_app
ARGS: {"app_name": "Spotify"}

TOOL: open_url_in_safari
ARGS: {"url": "https://www.youtube.com"}

TOOL: search_web
ARGS: {"query": "latest Apple news"}

TOOL: system_status
ARGS: {}

Rules:
- Never pretend an action happened.
- Choose the appropriate tool yourself.
- Understand natural language.
- YouTube, Google and websites are NOT macOS applications.
- "Open YouTube" means open_url_in_safari.
- "Open YouTube in Safari" means open_url_in_safari.
- "Open Spotify" means open_app.
- "Open Calculator" means open_app.
- "Search for X" means search_web.
- "What's my system status?" means system_status.
- If no tool is required, answer normally.
- Normal answers should be short.
- Never output a fake tool call.
- Output only ONE tool call when an action is required.
"""

conversation = []


def ask_jarvis(user_input: str) -> str:
    memory = get_all_memory()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "system",
            "content": f"USER MEMORY:\n{memory}",
        },
        *conversation[-6:],
        {
            "role": "user",
            "content": user_input,
        },
    ]

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": 0.1,
                "num_predict": 40,
            },
        },
        timeout=15,
    )

    response.raise_for_status()

    answer = response.json()["message"]["content"].strip()

    conversation.append({
        "role": "user",
        "content": user_input,
    })

    conversation.append({
        "role": "assistant",
        "content": answer,
    })

    return answer


def parse_tool_call(response: str):
    lines = response.splitlines()

    tool_name = None
    args = {}

    for line in lines:
        line = line.strip()

        if line.startswith("TOOL:"):
            tool_name = line[5:].strip()

        elif line.startswith("ARGS:"):
            try:
                args = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                return None

    if not tool_name:
        return None

    return {
        "name": tool_name,
        "args": args,
    }
