import json
from mlx_lm import load, generate

MODEL_PATH = "mlx-community/Qwen2.5-3B-Instruct-4bit"

print("🧠 Loading JARVIS MLX brain...")

model, tokenizer = load(MODEL_PATH)

print("🟢 JARVIS MLX brain ready.")

SYSTEM_PROMPT = """You are JARVIS, an autonomous AI assistant running locally on a Mac.

PERSONALITY:
- Calm, intelligent, confident and concise.
- British-style professional manner.
- Occasionally address the user as "sir".
- Never ramble.
- Never ask unnecessary follow-up questions.

AVAILABLE TOOLS:

research_web(query)
open_app(app_name)
close_app(app_name)
list_open_apps()
open_website(url)
open_url_in_safari(url)
search_web(query)
system_status()

TOOL FORMAT:

When a tool is required, output ONLY:

TOOL: tool_name
ARGS: {"argument": "value"}

Examples:

TOOL: open_app
ARGS: {"app_name": "Safari"}

TOOL: search_web
ARGS: {"query": "latest Apple news"}

TOOL: system_status
ARGS: {}

RULES:

- Never invent tools.
- Never pretend a tool was executed.
- Never explain a tool call.
- Use exactly ONE tool call when a tool is required.
- If no tool is required, respond naturally and concisely.
- Do not use tools for ordinary conversation.
- "Open Safari" means open_app.
- "Open Spotify" means open_app.
- "Open YouTube" means open_url_in_safari.
- "Search for X" means search_web.
- "Check my system" means system_status.
- "Research X" means research_web.
- Use research_web when the user asks for current information, comparisons, recommendations, financial research, news, or factual research that requires the web
"""

conversation = []

def ask_jarvis(user_input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    messages.extend(conversation[-6:])

    messages.append({
        "role": "user",
        "content": user_input,
    })

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=512,
        verbose=False,
    )

    answer = response.strip()

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
