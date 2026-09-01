from faster_whisper import WhisperModel

print("Loading Whisper...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Whisper ready.")

segments, info = model.transcribe("test.wav")

text = " ".join(segment.text for segment in segments)

print("\nYou said:")
print(text)
