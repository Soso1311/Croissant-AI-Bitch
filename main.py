import argparse
import string
import subprocess
import re
import warnings
import sys
import os
import ollama
from ddgs import DDGS
from core.voice import listen, speak

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

MODEL_NAME = "qwen2.5:7b"

# --- JARVIS AGENT TOOLS ---

def search_web(query: str) -> str:
"""Search the web for real-time information."""
print(f"\n🌐 [JARVIS searching web]: {query}")
try:
    results = list(DDGS().text(query, max_results=3))
    if not results:
        return "No web search results found."
    return "\n".join([f"Title: {r.get('title')}\nSnippet: {r.get('body')}" for r in results])
except Exception as e:
    return f"Search error: {e}"

def control_mac_system(action: str, parameter: str = "") -> str:
"""Control macOS volume, battery, apps, or open URLs."""
print(f"\n🛠️ [JARVIS controlling Mac]: {action} ({parameter})")
try:
    if action == "battery":
        return subprocess.check_output(["pmset", "-g", "batt"]).decode('utf-8')
    elif action == "set_volume":
        vol = int(parameter) if parameter.isdigit() else 50
        subprocess.run(["osascript", "-e", f"set volume output volume {vol}"])
        return f"Volume set to {vol}%."
    elif action == "open_app":
        subprocess.run(["open", "-a", parameter])
        return f"Opened application {parameter}."
    elif action == "open_url":
        subprocess.run(["open", parameter])
        return f"Opened URL {parameter}."
    elif action == "get_time":
        return subprocess.check_output(["date"]).decode('utf-8').strip()
    return "Unknown action."
except Exception as e:
    return f"System command failed: {e}"

def send_email_via_apple_mail(recipient: str, subject: str, body: str) -> str:
"""
Sends an email via macOS Apple Mail.
ONLY execute this tool when the user has explicitly confirmed recipient, subject, and body.
"""
print(f"\n📧 [JARVIS Sending Email to {recipient}]")
applescript = f'''
tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
    tell newMessage
        make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
        send
    end tell
end tell
'''
try:
    subprocess.run(["osascript", "-e", applescript], check=True)
    return f"Email successfully dispatched to {recipient}."
except Exception as e:
    return f"Failed to send email: {e}"

def run_python_automation(code: str) -> str:
"""Execute dynamic python automation scripts (Playwright, web scraping, file ops)."""
print(f"\n⚡ [JARVIS executing Python script...]")
script_path = "_temp_jarvis_task.py"
try:
    with open(script_path, "w") as f:
        f.write(code)
    
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    if os.path.exists(script_path):
        os.remove(script_path)

    output = result.stdout if result.stdout else result.stderr
    return output[:1000] if output else "Task completed successfully."
except Exception as e:
    if os.path.exists(script_path):
        os.remove(script_path)
    return f"Execution error: {e}"

AVAILABLE_TOOLS = [search_web, control_mac_system, send_email_via_apple_mail, run_python_automation]

def stream_and_speak(client, messages):
"""Streams LLM response tokens and speaks full sentences instantly."""
stream = client.chat(model=MODEL_NAME, messages=messages, stream=True)
sentence_buffer = ""
full_text = ""

for chunk in stream:
    token = chunk.get("message", {}).get("content", "")
    if not token:
        continue
    
    sentence_buffer += token
    full_text += token
    print(token, end="", flush=True)

    if re.search(r'[.!?]\s', sentence_buffer):
        match = re.search(r'^(.*?[.!?])\s*(.*)$', sentence_buffer, re.DOTALL)
        if match:
            sentence_to_speak = match.group(1).strip()
            sentence_buffer = match.group(2)
            if sentence_to_speak:
                speak(sentence_to_speak)

if sentence_buffer.strip():
    speak(sentence_buffer.strip())

print()
return full_text

def run_voice_agent():
print("=" * 60)
print(f"🤖 JARVIS AI System Active | Brain: '{MODEL_NAME}'")
print("=" * 60)

system_prompt = (
    "You are JARVIS, an autonomous, highly capable local AI assistant for macOS.\n\n"
    "INTERACTIVE DIRECTIVES:\n"
    "1. EMAIL INTERACTION: If the user asks to send an email, DO NOT immediately call `send_email_via_apple_mail`. "
    "First ask who to send it to, what the subject is, and what they want to say. "
    "Once you have all details, state the draft clearly and ask for explicit confirmation ('Shall I send this, sir?').\n"
    "2. TASK CLARIFICATION: If a request is vague or missing required parameters, ask smart clarification questions.\n"
    "3. SPOKEN RESPONSE TONE: Speak naturally, crisply, and directly (1-2 sentences at a time). Do not speak in bullet points or code blocks.\n"
    "4. EXECUTIONS: Never claim you cannot perform an action if a tool or Python script can accomplish it."
)

history = [{"role": "system", "content": system_prompt}]
speak("JARVIS system online. How can I assist you, sir?")

client = ollama.Client(timeout=60.0)

while True:
    try:
        raw_input = listen(pause_threshold=2.0, max_phrase_time=25)
        if not raw_input or not raw_input.strip():
            continue

        cleaned_input = raw_input.lower().translate(str.maketrans('', '', string.punctuation)).strip()
        if cleaned_input in {"exit", "quit", "stop", "goodbye", "power down", "standby"}:
            speak("Standing by, sir.")
            break

        history.append({"role": "user", "content": raw_input})

        if len(history) > 16:
            history = [history[0]] + history[-14:]

        response = client.chat(
            model=MODEL_NAME, 
            messages=history,
            tools=AVAILABLE_TOOLS
        )

        if response.message.tool_calls:
            history.append(response.message)
            
            for tool in response.message.tool_calls:
                fn_name = tool.function.name
                args = tool.function.arguments

                if fn_name == "search_web":
                    res = search_web(query=args.get("query", raw_input))
                elif fn_name == "control_mac_system":
                    res = control_mac_system(action=args.get("action", ""), parameter=str(args.get("parameter", "")))
                elif fn_name == "send_email_via_apple_mail":
                    res = send_email_via_apple_mail(
                        recipient=args.get("recipient", ""),
                        subject=args.get("subject", ""),
                        body=args.get("body", "")
                    )
                elif fn_name == "run_python_automation":
                    res = run_python_automation(code=args.get("code", ""))
                else:
                    res = "Action completed."

                history.append({"role": "tool", "content": res})

            assistant_reply = stream_and_speak(client, history)
        else:
            assistant_reply = stream_and_speak(client, history)

        history.append({"role": "assistant", "content": assistant_reply})

    except KeyboardInterrupt:
        speak("Powering down, sir.")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("I encountered an issue processing that request.")

if __name__ == "__main__":
parser = argparse.ArgumentParser(description="JARVIS Voice Assistant")
parser.add_argument("--voice", action="store_true", help="Start voice mode")
args = parser.parse_args()

if args.voice or len(sys.argv) == 1:
    run_voice_agent()
else:
    print("Run with '--voice' to start voice mode.")
