import subprocess
from faster_whisper import WhisperModel
import pyttsx3


# -----------------------------
# WHISPER
# -----------------------------

print("Loading Whisper...")

whisper = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Whisper ready.")


# -----------------------------
# TEXT TO SPEECH
# -----------------------------

tts = pyttsx3.init()

tts.setProperty("rate", 175)
tts.setProperty("volume", 1.0)


# -----------------------------
# JARVIS BRAIN
# -----------------------------

SYSTEM_PROMPT = """
You are JARVIS, an advanced AI assistant inspired by Iron Man.

You are calm, intelligent, concise and slightly witty.

Speak naturally like a sophisticated British AI assistant.

Do not over-explain simple things.

Occasionally address the user as sir, but do not overuse it.
"""


def ask_jarvis(text):

    prompt = f"""
{SYSTEM_PROMPT}

USER:
{text}

JARVIS:
"""

    result = subprocess.run(
        ["ollama", "run", "mistral:latest", prompt],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "I'm afraid something went wrong, sir."

    return result.stdout.strip()


# -----------------------------
# SPEAK
# -----------------------------

def speak(text):

    print(f"\nJARVIS: {text}\n")

    tts.say(text)
    tts.runAndWait()


# -----------------------------
# MAIN
# -----------------------------

def main():

    print("""
╔════════════════════════════════════╗
║            J A R V I S             ║
║          VOICE SYSTEM ONLINE       ║
╚════════════════════════════════════╝
""")

    while True:

        input("Press ENTER and speak...")

        print("🎙️ Listening...")

        # Record 5 seconds using the existing mic test
        subprocess.run(["python", "mic_test.py"])

        segments, info = whisper.transcribe("test.wav")

        text = " ".join(
            segment.text for segment in segments
        ).strip()

        if not text:
            continue

        print(f"\nYOU: {text}")

        if text.lower() in ["exit", "quit", "shutdown", "goodbye"]:

            speak("Shutting down, sir.")

            break

        response = ask_jarvis(text)

        speak(response)


if __name__ == "__main__":
    main()
