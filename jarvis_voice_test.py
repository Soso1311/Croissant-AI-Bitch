from pathlib import Path
from piper import PiperVoice
import wave

MODEL = Path("voices/jarvis/en/en_GB/jarvis/medium/jarvis-medium.onnx")

voice = PiperVoice.load(str(MODEL))

text = "Good evening, sir. How may I be of assistance?"

print("JARVIS is speaking...")

with wave.open("jarvis_test.wav", "wb") as wav:
    voice.synthesize_wav(text, wav)

print("Done. Playing JARVIS...")

import subprocess
subprocess.run(["afplay", "jarvis_test.wav"])
