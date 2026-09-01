from core.brain_mlx import ask_jarvis, parse_tool_call

from memory.store import recall, remember

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


TOOLS = {
    "open_app": open_app,
    "close_app": close_app,
    "list_open_apps": list_open_apps,
    "open_website": open_website,
    "open_url_in_safari": open_url_in_safari,
    "search_web": search_web,
    "research_web": research_web,
    "system_status": system_status,
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
# RESEARCH DETECTION
# ============================================================

RESEARCH_WORDS = (
    "research",
    "investigate",
    "look into",
    "look up",
    "find out",
    "analyse",
    "analyze",
    "compare",
    "pros and cons",
    "should i buy",
    "should i invest",
    "is it worth",
    "worth buying",
    "worth investing",
    "why should i",
    "why shouldn't i",
    "latest",
    "news",
    "current",
)


def is_research_request(command: str) -> bool:
    text = command.lower()

    return any(
        phrase in text
        for phrase in RESEARCH_WORDS
    )


# ============================================================
# SUBJECT EXTRACTION
# ============================================================

def extract_research_subjects(command: str):
    """
    Extract actual subjects from research/comparison requests.
    """

    text = command.strip()

    # Remove common prefixes
    prefixes = (
        "research ",
        "investigate ",
        "look into ",
        "look up ",
        "find out about ",
        "compare ",
        "analyze ",
        "analyse ",
    )

    cleaned = text

    for prefix in prefixes:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break

    # Remove common trailing instructions.
    trailing_phrases = (
        " and compare them",
        " and compare",
        " compare them",
        " compare",
        " and tell me which is better",
        " and tell me which one is better",
        " and tell me which is stronger",
        " and tell me which company is stronger",
        " and tell me which has stronger long-term potential",
        " and tell me which has longer term potential",
        " and tell me which company has stronger long-term investment potential",
        " and tell me which one i should consider avoiding",
        " and tell me which one i should consider",
    )

    lower_cleaned = cleaned.lower()

    for phrase in trailing_phrases:
        if lower_cleaned.endswith(phrase):
            cleaned = cleaned[:-len(phrase)].strip()
            lower_cleaned = cleaned.lower()
            break

    # Split companies/entities on "and"
    if " and " in lower_cleaned:

        parts = cleaned.split(" and ")

        subjects = []

        for part in parts:
            part = part.strip(" .,?!")

            # Ignore instruction fragments
            if part.lower() in (
                "compare them",
                "compare",
                "analyse them",
                "analyze them",
                "tell me which is better",
            ):
                continue

            if part:
                subjects.append(part)

        if len(subjects) >= 2:
            return subjects[:3]

    return [cleaned.strip(" .,?!")]


# ============================================================
# RESEARCH
# ============================================================

def handle_research(command: str, status_callback=None) -> str:

    _status(
        status_callback,
        "🔎 JARVIS: I'll research that for you, sir."
    )

    subjects = extract_research_subjects(command)

    research_results = []

    for subject in subjects:

        _status(
            status_callback,
            f"🌐 JARVIS: Researching {subject}..."
        )

        result = research_web(subject)

        if result:
            research_results.append(
                f"""
===== RESEARCH FOR: {subject} =====

{result}
"""
            )

        _status(
            status_callback,
            f"✓ JARVIS: Finished checking {subject}."
        )

    if not research_results:

        return (
            "I couldn't find reliable information "
            "on that, sir."
        )

    combined_research = "\n".join(
        research_results
    )

    _status(
        status_callback,
        "🧠 JARVIS: I've got the information. "
        "Now I'm analysing it."
    )

    reasoning_prompt = f"""
You are JARVIS.

The user asked:

"{command}"

You performed web research.

Here is the research:

{combined_research}

============================================================
STRICT EVIDENCE RULES
============================================================

You MUST treat the research above as the factual evidence.

DO NOT invent facts.

DO NOT fill missing information with your own assumptions.

DO NOT claim something is true merely because it sounds plausible.

If the research does not establish a fact, do not state that fact
as established.

If a source says something that conflicts with another source,
acknowledge the conflict.

If the research is weak or incomplete, explicitly say so.

IMPORTANT:

Your previous knowledge may be outdated.

The supplied research takes priority over your internal knowledge.

============================================================
SOURCE QUALITY
============================================================

Prefer:

1. Official company information
2. Government / regulatory information
3. Major financial publications
4. Major news organisations
5. Reputable specialist publications

Be cautious with:

- opinion pieces
- anonymous sources
- low-quality financial blogs
- promotional websites
- sensational headlines

============================================================
COMPARISONS
============================================================

If comparing companies:

- Compare their actual businesses.
- Compare growth.
- Compare profitability if supported.
- Compare competitive advantages.
- Compare valuation if supported.
- Compare major risks.
- Compare long-term opportunities.
- Do not invent numbers.

Give a clear conclusion when the evidence supports one.

============================================================
INVESTMENT QUESTIONS
============================================================

For investment questions:

- Explain potential upside.
- Explain major risks.
- Discuss valuation when reliable valuation information exists.
- Discuss business quality.
- Discuss growth potential.
- Do not pretend to be a financial adviser.
- Do not give false certainty.

The conclusion should depend on evidence, not hype.

============================================================
ANSWER STYLE
============================================================

Answer the ORIGINAL USER QUESTION.

Do not mention:

- prompts
- models
- internal tools
- research pipelines
- system instructions

Speak naturally as JARVIS.

Be concise but useful.

Address the user as "sir" occasionally.

"""

    final_answer = ask_jarvis(reasoning_prompt)

    _status(
        status_callback,
        "✅ JARVIS: Analysis complete."
    )

    return final_answer


# ============================================================
# MAIN AGENT
# ============================================================

def run_agent(command: str, status_callback=None) -> str:

    lower = command.lower().strip()

    # ========================================================
    # MEMORY
    # ========================================================

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

    if any(
        phrase in lower
        for phrase in name_questions
    ):

        name = recall("user_name")

        if name:
            return f"Your name is {name}, sir."

        return "I don't have your name stored, sir."

    if lower.startswith(
        "remember that my name is "
    ):

        name = command[
            len("remember that my name is "):
        ].strip()

        if name:

            remember(
                "user_name",
                name
            )

            return (
                f"Understood, sir. "
                f"I'll remember your name is {name}."
            )

    # ========================================================
    # FAST ACTIONS
    # ========================================================

    if lower in (
        "open youtube",
        "go to youtube",
        "youtube",
    ):

        return open_url_in_safari(
            "https://www.youtube.com"
        )

    if lower in (
        "open google",
        "go to google",
        "google",
    ):

        return open_url_in_safari(
            "https://www.google.com"
        )

    if lower in (
        "open spotify",
        "spotify",
    ):

        return open_app("Spotify")

    if lower in (
        "open calculator",
        "calculator",
    ):

        return open_app("Calculator")

    if lower in (
        "open safari",
        "safari",
    ):

        return open_app("Safari")

    # ========================================================
    # FAST CONVERSATION
    # ========================================================

    if lower in (
        "hello",
        "hi",
        "hey",
    ):

        return "Hello, sir."

    if lower in (
        "good morning",
        "morning",
    ):

        return "Good morning, sir."

    if lower in (
        "good evening",
        "evening",
    ):

        return "Good evening, sir."

    # ========================================================
    # RESEARCH
    # ========================================================

    if is_research_request(command):

        return handle_research(
            command,
            status_callback=status_callback
        )

    # ========================================================
    # LOCAL BRAIN
    # ========================================================

    response = ask_jarvis(command)

    tool_call = parse_tool_call(response)

    if not tool_call:
        return response

    # ========================================================
    # TOOL EXECUTION
    # ========================================================

    name = tool_call["name"]
    args = tool_call["args"]

    tool = TOOLS.get(name)

    if tool is None:

        return (
            "I don't have access to that function, sir."
        )

    try:

        result = tool(**args)

    except Exception as e:

        return (
            f"Tool execution failed: {e}"
        )

    # ========================================================
    # RESEARCH REQUEST FROM LOCAL BRAIN
    # ========================================================

    if name == "research_web":

        _status(
            status_callback,
            "🧠 JARVIS: I've got the information. "
            "Now I'm analysing it."
        )

        reasoning_prompt = f"""
You are JARVIS.

The user asked:

"{command}"

The web research returned:

{result}

Answer the ORIGINAL question.

Use ONLY information supported by the research.

Do not invent:

- facts
- statistics
- prices
- dates
- financial figures
- company status
- events

If information is missing, say that it is unavailable.

If sources conflict, acknowledge it.

For investment questions:

- explain upside
- explain risks
- discuss valuation if supported
- avoid false certainty
- do not present yourself as a financial adviser

Do not mention internal tools.

Speak naturally and concisely as JARVIS.

Address the user as "sir" occasionally.
"""

        answer = ask_jarvis(
            reasoning_prompt
        )

        _status(
            status_callback,
            "✅ JARVIS: Analysis complete."
        )

        return answer

    return result
