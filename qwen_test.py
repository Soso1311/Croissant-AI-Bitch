from mlx_audio.tts import load
import soundfile as sf
import numpy as np

print("Loading JARVIS...")

model = load(
    "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit"
)

text = """
Good evening, sir. All systems are operational.
How may I be of assistance?
"""

voice_description = """
A sophisticated British male AI assistant.
Deep, smooth and resonant baritone.
Extremely natural human speech.
No robotic or synthetic quality.
Precise, polished British pronunciation.
Calm, intelligent and composed.
Subtle warmth with restrained emotion.
Confident and authoritative without sounding aggressive.
Measured cinematic pacing with natural pauses.
High-end professional studio recording.
"""

print("Generating voice...")

generator = model.generate_voice_design(
    text=text,
    instruct=voice_description,
)

audio_chunks = []

for result in generator:
    if hasattr(result, "audio"):
        audio_chunks.append(np.asarray(result.audio))
    elif isinstance(result, tuple):
        audio_chunks.append(np.asarray(result[0]))
    else:
        audio_chunks.append(np.asarray(result))

audio = np.concatenate(audio_chunks)

print("Generation complete.")
print("Audio shape:", audio.shape)

sf.write(
    "qwen_jarvis.wav",
    audio,
    24000
)

print("Saved qwen_jarvis.wav")


