import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("JARVIS_MODEL", "qwen2.5:7b")

STRICT_SANDBOX_MODE = True  
BLOCKED_COMMANDS = [
    "rm -rf /", "rm -rf ~", "mkfs", "dd", "shutdown", "reboot",
    ":(){ :|:& };:", "chmod -R 777 /", "sudo rm -rf"
]

STT_MODEL_SIZE = "base.en"
TTS_VOICE = "af_heart"
SAMPLE_RATE = 24000
