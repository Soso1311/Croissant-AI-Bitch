from core.brain_mlx import ask_jarvis, parse_tool_call

from memory.store import remember, recall

from tools.apps import (
    open_app,
    close_app,
    list_open_apps,
)

from tools.web import (
    open_website,
    open_url_in_safari,
    search_web,
    research_web,
)

from tools.system import system_status


MAX_TOOL_ITERATIONS = 5


def _memory_remember(key: str, value: str) -> str:
    remember(key, value)
    return f"Remembered {key}: {value}"


def _memory_recall(key: str) -> str:
    value = recall(key)
    if value is None:
        return f"No stored value for '{key}'."
    return f"{key}: {value}"


TOOLS = {
    "open_app": open_app,
    "close_app": close_app,
    "list_open_apps": list_open_apps,
    "open_website": open_website,
    "open_url_in_safari": open_url_in_safari,
    "search_web": search_web,
    "research_web": research_web,
    "system_status": system_status,
    "remember": _memory_remember,
    "recall": _memory_recall,
}


# ============================================================
# STATUS
# ============================================================

def _status(callback, message):
    print(message)

    if callback:
        try:
            callback(message)
        except Exception:
            pass


# ============================================================
# MAIN AGENT
# ============================================================
#
# understand -> decide if a tool is needed -> execute -> observe ->
# reason -> (repeat if needed) -> answer.
#
# No keyword/phrase routing here on purpose. core/brain_mlx.py's system
# prompt already tells the model what tools exist and when to use them —
# this loop just executes whatever the model decides and feeds the result
# back for another round, up to MAX_TOOL_ITERATIONS.

def run_agent(command: str, status_callback=None) -> str:

    current_input = command

    for _ in range(MAX_TOOL_ITERATIONS):

        response = ask_jarvis(current_input)
        call = parse_tool_call(response)

        if call is None:
            return response

        name = call["name"]
        args = call["args"]

        tool = TOOLS.get(name)

        if tool is None:
            return f"I tried to use a tool called '{name}', but I don't have that, sir."

        subject = (
            args.get("query")
            or args.get("app_name")
            or args.get("url")
            or args.get("key")
            or ""
        )

        _status(
            status_callback,
            f"⚙️ JARVIS: Using {name}" + (f" — {subject}..." if subject else "...")
        )

        try:
            result = tool(**args)
        except Exception as e:
            result = f"Tool '{name}' failed: {e}"

        _status(status_callback, f"✓ JARVIS: Done with {name}.")

        current_input = (
            f"TOOL RESULT ({name}):\n{result}\n\n"
            f'Using this result, answer the user\'s original request: "{command}"\n'
            "If this fully answers it, give your final answer now in plain "
            "text (no TOOL: line). If you still need another tool "
            "(e.g. a second subject to research), call it."
        )

    return (
        "I've gathered what I can, sir, but I want to stop here rather "
        "than keep going in circles."
    )
