import pyautogui
import base64
import json
import time
import subprocess
import mss
from PIL import Image
import io
import os
import re

# ============ CONFIG (local Ollama) ============
MODEL = "llava:7b"          # free vision model you already have

# ============ SCREEN CAPTURE ============
def capture_screen():
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=50)
        return base64.b64encode(buffered.getvalue()).decode()

# ============ ACTIONS ============
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
}

# ============ LOCAL LLM ENGINE (Ollama) ============
def ask_llm_what_to_do(user_command, screenshot_b64):
    prompt = f"""
    User command: "{user_command}"
    
    Current screen attached. Decide the next action.
    Return ONLY JSON: {{"action": "action_name", "params": {{...}} }}
    
    Available actions:
    - move_mouse: {{"x": int, "y": int}}
    - click: {{}}
    - double_click: {{}}
    - right_click: {{}}
    - scroll: {{"amount": int}}
    - type_text: {{"text": "string"}}
    - press_key: {{"key": "enter|tab|space"}}
    - hotkey: {{"keys": "ctrl+c"}}
    - drag: {{"x": int, "y": int}}
    
    If done, return {{"done": true, "message": "Task completed"}}
    """
    
    # Save screenshot temporarily
    img_data = base64.b64decode(screenshot_b64)
    with open("/tmp/screen.jpg", "wb") as f:
        f.write(img_data)
    
    # Call Ollama (vision model)
    cmd = ["ollama", "run", MODEL, prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout
    except subprocess.TimeoutExpired:
        print("  ⏱️ Ollama timeout – try simpler command")
        return None
    
    # Extract JSON from answer
    json_match = re.search(r'\{.*\}', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            return None
    return None

# ============ MAIN LOOP ============
def run_until_done(user_command, max_steps=20):
    print(f"🎯 Executing: {user_command}")
    print("Press Ctrl+C to abort\n")
    
    step = 0
    while step < max_steps:
        step += 1
        print(f"  Step {step}: thinking...")
        screenshot = capture_screen()
        decision = ask_llm_what_to_do(user_command, screenshot)
        
        if not decision:
            print("❌ No valid response from LLM")
            break
            
        if decision.get("done"):
            print(f"✅ {decision.get('message', 'Done!')}")
            break
            
        action = decision.get("action")
        params = decision.get("params", {})
        
        if action in ACTIONS:
            print(f"  ▶️  {action} {params}")
            try:
                if action == "move_mouse":
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
                time.sleep(0.5)
            except Exception as e:
                print(f"  ❌ Action failed: {e}")
        else:
            print(f"  ⚠️ Unknown action: {action}")
            
        # No keyboard module, just use simple interrupt
        # (press Ctrl+C to stop)

# ============ CLI ============
if __name__ == "__main__":
    print("🤖 LLM Computer Controller (local Ollama)")
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
