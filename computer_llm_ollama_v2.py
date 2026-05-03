import pyautogui
import base64
import json
import time
import subprocess
import mss
from PIL import Image
import io
import re
import os

# ============ CONFIG ============
MODEL = "llama3.2-vision:11b"          # your local vision model
DEMO_MODE = False            # Set to False to use real LLM

# ============ SCREEN CAPTURE ============
def capture_screen():
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=50)
        return base64.b64encode(buffered.getvalue()).decode()

# ============ ACTIONS (expanded) ============
def open_app(app_name):
    # macOS
    subprocess.run(["open", "-a", app_name])
    time.sleep(1)

ACTIONS = {
    "move_mouse": lambda x, y: pyautogui.moveTo(x, y),
    "click": lambda: pyautogui.click(),
    "double_click": lambda: pyautogui.doubleClick(),
    "right_click": lambda: pyautogui.rightClick(),
    "scroll": lambda amount: pyautogui.scroll(amount),
    "type_text": lambda text: pyautogui.write(text),
    "press_key": lambda key: pyautogui.press(key),
    "hotkey": lambda keys: pyautogui.hotkey(*keys.split('+')),
    "drag": lambda x, y: pyautogui.drag(x, y),
    "open_app": open_app,
    "wait": lambda seconds: time.sleep(float(seconds)),
}

# ============ LLM ENGINE (with demo mode) ============
def ask_llm_what_to_do(user_command, screenshot_b64):
    if DEMO_MODE:
        # Hardcoded sequence for common commands
        cmd = user_command.lower()
        if "open safari" in cmd:
            return {"action": "open_app", "params": {"app_name": "Safari"}}
        elif "open opera" in cmd:
            return {"action": "open_app", "params": {"app_name": "Opera GX"}}
        elif "youtube" in cmd and "type" not in cmd:
            return {"action": "type_text", "params": {"text": "youtube.com"}}
        elif "press enter" in cmd or "go to" in cmd:
            return {"action": "press_key", "params": {"key": "enter"}}
        elif "click" in cmd:
            return {"action": "click", "params": {}}
        elif "type" in cmd:
            return {"action": "type_text", "params": {"text": "Hello from AI"}}
        else:
            return {"done": True, "message": "Demo command complete"}
    
    # ---------- REAL OLLAMA PROMPT ----------
    prompt = f"""You control the computer. Given the user command and the current screen, decide the **single next action**.
Return ONLY valid JSON. No extra text.

Available actions and their JSON format:
- move_mouse: {{"action": "move_mouse", "params": {{"x": int, "y": int}}}}
- click: {{"action": "click", "params": {{}}}}
- double_click: {{"action": "double_click", "params": {{}}}}
- right_click: {{"action": "right_click", "params": {{}}}}
- scroll: {{"action": "scroll", "params": {{"amount": int}}}}
- type_text: {{"action": "type_text", "params": {{"text": "string"}}}}
- press_key: {{"action": "press_key", "params": {{"key": "enter|tab|space|backspace"}}}}
- hotkey: {{"action": "hotkey", "params": {{"keys": "ctrl+c"}}}}
- open_app: {{"action": "open_app", "params": {{"app_name": "Safari"}}}}
- wait: {{"action": "wait", "params": {{"seconds": 1}}}}

If the command is finished, return: {{"done": true, "message": "Done"}}

User command: "{user_command}"
Now decide the next action based on the screenshot.
"""
    # Save screenshot temporarily
    img_data = base64.b64decode(screenshot_b64)
    with open("/tmp/screen.jpg", "wb") as f:
        f.write(img_data)
    
    # Call Ollama
    cmd = ["ollama", "run", MODEL, prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
        output = result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("  ⏱️ Ollama timeout")
        return None
    
    # Try to extract JSON
    json_match = re.search(r'\{.*\}', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    # Fallback for simple commands
    if "click" in user_command.lower():
        return {"action": "click", "params": {}}
    return None

# ============ MAIN LOOP (fixed) ============
def run_until_done(user_command, max_steps=8):
    print(f"🎯 Executing: {user_command}")
    print("Press Ctrl+C to abort\n")

    last_action = None
    repeat_count = 0
    step = 0

    while step < max_steps:
        step += 1
        print(f"  Step {step}: thinking...")
        screenshot = capture_screen()
        decision = ask_llm_what_to_do(user_command, screenshot)

        if not decision:
            print("❌ No valid response. Stopping.")
            break

        if decision.get("done"):
            print(f"✅ {decision.get('message', 'Done!')}")
            break

        action = decision.get("action")
        params = decision.get("params", {})

        # Detect repeated same action (infinite loop)
        current_key = f"{action}_{params}"
        if current_key == last_action:
            repeat_count += 1
            if repeat_count >= 2:
                print("⚠️ Same action repeated twice. Assuming task complete.")
                break
        else:
            repeat_count = 0
            last_action = current_key

        if action in ACTIONS:
            print(f"  ▶️  {action} {params}")
            try:
                if action == "open_app":
                    ACTIONS[action](params["app_name"])
                elif action == "wait":
                    ACTIONS[action](params["seconds"])
                elif action == "move_mouse":
                    ACTIONS[action](params["x"], params["y"])
                elif action == "drag":
                    ACTIONS[action](params["x"], params["y"])
                elif action == "scroll":
                    ACTIONS[action](params["amount"])
                elif action == "type_text":
                    ACTIONS[action](params["text"])
                elif action == "press_key":
                    ACTIONS[action](params["key"])
                elif action == "hotkey":
                    ACTIONS[action](params["keys"])
                else:
                    ACTIONS[action]()
                time.sleep(0.7)
            except Exception as e:
                print(f"  ❌ Action failed: {e}")
                break
        else:
            print(f"  ⚠️ Unknown action: {action}")
            break

    if step >= max_steps:
        print(f"⏹️ Reached max steps ({max_steps}). Stopping.")

# ============ CLI ============
if __name__ == "__main__":
    print("🤖 LLM Computer Controller (local Ollama v2)")
    print("=" * 50)
    print("⚠️  This AI will control your mouse and keyboard.")
    print("   Press Ctrl+C to stop at any time.\n")

    input("Press Enter to continue...")

    while True:
        try:
            command = input("\n💬 What should the AI do? > ")
            if command.lower() in ['quit', 'exit', 'q']:
                break
            run_until_done(command)
            print("\n" + "="*50)
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
            break
