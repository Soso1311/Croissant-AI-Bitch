from core.brain_mlx import ask_jarvis, parse_tool_call
from memory.store import recall, remember
from tools.apps import open_app, close_app, list_open_apps
from tools.web import open_website, open_url_in_safari, search_web
from tools.system import system_status


TOOLS = {
    "open_app": open_app,
    "close_app": close_app,
    "list_open_apps": list_open_apps,
    "open_website": open_website,
    "open_url_in_safari": open_url_in_safari,
    "search_web": search_web,
    "system_status": system_status,
}


def run_agent(command: str) -> str:
    lower = command.lower().strip()

    # =========================
    # MEMORY
    # =========================

    name_questions = (
        "what's my name",
        "what is my name",
        "whats my name",
        "tell me my name",
        "tell me what my name is",
        "do you know my name",
        "do you remember my name",
        "remind me my name",
        "remind me what my name is",
        "who am i",
    )

    if any(phrase in lower for phrase in name_questions):
        name = recall("user_name")

        if name:
            return f"Your name is {name}, sir."

        return "I don't have your name stored, sir."

    if lower.startswith("remember that my name is "):
        name = command[len("remember that my name is "):].strip()

        if name:
            remember("user_name", name)
            return f"Understood, sir. I'll remember your name is {name}."

    # FAST ACTIONS
    if lower in ("open youtube", "go to youtube", "youtube"):
        return open_url_in_safari("https://www.youtube.com")

    if lower in ("open google", "go to google", "google"):
        return open_url_in_safari("https://www.google.com")

    if lower in ("open spotify", "spotify"):
        return open_app("Spotify")

    if lower in ("open calculator", "calculator"):
        return open_app("Calculator")

    if lower in ("open safari", "safari"):
        return open_app("Safari")

    # FAST CONVERSATION
    if lower in ("hello", "hi", "hey"):
        return "Hello, sir."

    if lower in ("good morning", "morning"):
        return "Good morning, sir."

    if lower in ("good evening", "evening"):
        return "Good evening, sir."

    # LOCAL BRAIN
    response = ask_jarvis(command)

    # TOOL EXECUTION
    tool_call = parse_tool_call(response)

    if tool_call:
        name = tool_call["name"]
        args = tool_call["args"]

        tool = TOOLS.get(name)

        if tool is None:
            return "I don't have access to that function, sir."

        try:
            return tool(**args)
        except Exception as e:
            return f"Tool execution failed: {e}"

    return response
