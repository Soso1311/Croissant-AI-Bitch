cat > computer_llm_local.py << 'EOF'
import pyautogui
import base64
import json
import time
import subprocess
import mss
from PIL import Image
import io
import os

# ============ CONFIG FOR LOCAL OLLAMA ============
MODEL = "llava:7b"  # Free, runs locally

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
    
    # Save screenshot to temp file
    img_data = base64.b64decode(screenshot_b64)
    with open("/tmp/screen.jpg", "wb") as f:
        f.write(img_data)
    
    # Call Ollama with image
    cmd = ["ollama", "run", MODEL, prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    import re
    json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return None

# Rest of the code is the SAME as before (ACTIONS, run_until_done, etc.)
# Just copy from your original computer_llm.py but replace the ask_llm_what_to_do function
EOF
