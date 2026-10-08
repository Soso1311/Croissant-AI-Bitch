import subprocess
import speech_recognition as sr

def speak(text: str):
"""Native macOS TTS - fast, offline, zero-latency delivery."""
if not text or not text.strip():
    return
clean_text = text.replace('"', '\\"').replace("'", "\\'")
subprocess.run(["say", "-v", "Samantha", clean_text], check=False)

def listen(energy_threshold: int = 300, pause_threshold: float = 2.0, max_phrase_time: int = 25) -> str:
"""
Dynamic silence-detection microphone capture.
Holds the listening channel open through natural pauses (up to 2.0s of silence).
"""
r = sr.Recognizer()
r.energy_threshold = energy_threshold
r.dynamic_energy_threshold = True
r.pause_threshold = pause_threshold

with sr.Microphone() as source:
    print("\n🎙️ [JARVIS Listening...]")
    r.adjust_for_ambient_noise(source, duration=0.5)
    try:
        audio = r.listen(source, timeout=10, phrase_time_limit=max_phrase_time)
        print("⚡ Processing speech...")
        transcript = r.recognize_google(audio)
        print(f"🗣️ You said: '{transcript}'")
        return transcript
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print(f"⚠️ Mic error: {e}")
        return ""
