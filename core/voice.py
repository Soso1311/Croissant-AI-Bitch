import soundfile as sf
from kokoro_onnx import Kokoro
import sounddevice as sd

MODEL_PATH = "voices/kokoro/kokoro-v1.0.onnx"
VOICES_PATH = "voices/kokoro/voices-v1.0.bin"

print("Loading JARVIS voice...")

kokoro = Kokoro(
    MODEL_PATH,
    VOICES_PATH
)

VOICE = "am_onyx"
SPEED = 0.96
LANGUAGE = "en-us"

print("🟢 JARVIS voice ready.")


def speak(text: str):
    if not text:
        return

    try:
        print(f"🔊 JARVIS: {text}")

        samples, sample_rate = kokoro.create(
            text,
            voice=VOICE,
            speed=SPEED,
            lang=LANGUAGE
        )

        sd.play(samples, sample_rate)
        sd.wait()

    except Exception as e:
        print(f"❌ Voice error: {e}")
