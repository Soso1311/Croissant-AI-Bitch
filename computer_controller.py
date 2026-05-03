import pyautogui
import base64
import json
import time
import subprocess
import mss
from PIL import Image
import io
import re
import webbrowser

MODEL = "llama3.2-vision:11b"

def capture_screen():
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=50)
        return base64.b64encode(buffered.getvalue()).decode()

def open_app(app_name):
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
    "open_app": open_app,
    "open_url": lambda url: webbrowser.open(url),
    "wait": lambda seconds: time.sleep(float(seconds)),
}

def ask_llm_what_to_do(user_command, screenshot_b64):
    prompt = f"""Output ONLY valid JSON. No other text.

User command: "{user_command}"

Actions:
- open_app: {{"action": "open_app", "params": {{"app_name": "Safari"}}}}
- open_url: {{"action": "open_url", "params": {{"url": "https://gmail.com"}}}}
- click: {{"action": "click", "params": {{}}}}
- type_text: {{"action": "type_text", "params": {{"text": "hello"}}}}
- press_key: {{"action": "press_key", "params": {{"key": "enter"}}}}

If done: {{"done": true}}

Output JSON now:"""
    
    img_data = base64.b64decode(screenshot_b64)
    with open("/tmp/screen.jpg", "wb") as f:
        f.write(img_data)
    
    try:
        result = subprocess.run(["ollama", "run", MODEL, prompt], capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
    except:
        return None
    
    json_match = re.search(r'\{.*\}', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    cmd = user_command.lower()
    if "gmail" in cmd:
        return {"action": "open_url", "params": {"url": "https://mail.google.com"}}
    if "youtube" in cmd:
        return {"action": "open_url", "params": {"url": "https://youtube.com"}}
    if "opera" in cmd:
        return {"action": "open_app", "params": {"app_name": "Opera GX"}}
    if "safari" in cmd:
        return {"action": "open_app", "params": {"app_name": "Safari"}}
    if "click" in cmd:
        return {"action": "click", "params": {}}
    
    return {"done": True}

def run_until_done(user_command, max_steps=8):
    print(f"Executing: {user_command}")
    last_action = None
    repeat_count = 0
    
    for step in range(max_steps):
        print(f"Step {step+1}: thinking...")
        screenshot = capture_screen()
        decision = ask_llm_what_to_do(user_command, screenshot)
        
        if not decision or decision.get("done"):
            print("Done!")
            break
        
        action = decision.get("action")
        params = decision.get("params", {})
        
        action_key = f"{action}_{params}"
        if action_key == last_action:
            repeat_count += 1
            if repeat_count >= 2:
                print(f"Action '{action}' repeated, stopping")
                break
        else:
            repeat_count = 0
            last_action = action_key
        
        if action in ACTIONS:
            print(f"  {action}: {params}")
            try:
                if action == "open_app":
                    ACTIONS[action](params["app_name"])
                elif action == "open_url":
                    ACTIONS[action](params["url"])
                elif action == "move_mouse":
                    ACTIONS[action](params["x"], params["y"])
                elif action == "type_text":
                    ACTIONS[action](params["text"])
                elif action == "press_key":
                    ACTIONS[action](params["key"])
                else:
                    ACTIONS[action]()
                time.sleep(0.7)
            except Exception as e:
                print(f"Failed: {e}")
                break
        else:
            print(f"Unknown: {action}")
            break

if __name__ == "__main__":
    print("LLM Computer Controller")
    print("Type 'quit' to exit\n")
    while True:
        command = input("What should the AI do? > ")
        if command.lower() in ['quit', 'exit', 'q']:
            break
        run_until_done(command)
        print()
