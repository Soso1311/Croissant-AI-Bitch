import soundfile as sf
from kokoro_onnx import Kokoro

kokoro = Kokoro(
    "voices/kokoro/kokoro-v1.0.onnx",
    "voices/kokoro/voices-v1.0.bin"
)

text = "Good evening, sir. All systems are operational."

voices = [
    "am_michael",
    "am_echo",
    "am_onyx",
    "am_fenrir",
    "bm_lewis",
]

for voice in voices:
    samples, sample_rate = kokoro.create(
        text,
        voice=voice,
        speed=1.0,
        lang="en-us" if voice.startswith("am_") else "en-gb"
    )

    filename = f"test_{voice}.wav"
    sf.write(filename, samples, sample_rate)
    print(f"Generated {filename}")
