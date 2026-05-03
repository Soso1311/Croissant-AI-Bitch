import pyautogui
import base64
import json
import time
import keyboard
from openai import OpenAI
import mss
from PIL import Image
import io
import os

# ============ CONFIG ============
# Get API key from environment variable for safety
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("❌ Please set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-key-here'")
    exit(1)

client = OpenAI(api_key=API_KEY)
MODEL = "gpt-3.5-turbo"

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

# ============ LLM ENGINE ============
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

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You control computer. Return ONLY JSON."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}}
            ]}
        ],
        temperature=0.1,
        max_tokens=200
    )
    
    import re
    json_match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return None

# ============ MAIN LOOP ============
def run_until_done(user_command, max_steps=20):
    print(f"🎯 Executing: {user_command}")
    print("Press ESC to abort\n")
    
    step = 0
    while step < max_steps:
        step += 1
        screenshot = capture_screen()
        decision = ask_llm_what_to_do(user_command, screenshot)
        
        if not decision:
            print("❌ Invalid response")
            break
            
        if decision.get("done"):
            print(f"✅ {decision.get('message', 'Done!')}")
            break
            
        action = decision.get("action")
        params = decision.get("params", {})
        
        if action in ACTIONS:
            print(f"  Step {step}: {action} {params}")
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
                print(f"  ❌ Failed: {e}")
        else:
            print(f"  ⚠️ Unknown: {action}")
            
        if keyboard.is_pressed('esc'):
            print("⏹️ Aborted")
            break

# ============ CLI ============
if __name__ == "__main__":
    print("🤖 LLM Computer Controller")
    print("=" * 40)
    print("⚠️  WARNING: This AI will control your mouse/keyboard")
    input("Press Enter to continue...")
    
    while True:
        command = input("\n💬 What should the AI do? > ")
        if command.lower() in ['quit', 'exit', 'q']:
            break
        run_until_done(command)
        print("\n" + "="*40)
