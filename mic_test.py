import sounddevice as sd
import soundfile as sf

duration = 5
sample_rate = 16000

print("🎙️ Recording for 5 seconds...")
audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32",
    device=0
)

sd.wait()

sf.write("test.wav", audio, sample_rate)

print("✅ Saved recording as test.wav")
