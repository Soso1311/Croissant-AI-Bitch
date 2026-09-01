from openwakeword.model import Model
import sounddevice as sd
import numpy as np

model = Model(wakeword_models=["hey_jarvis"])

print("🟢 JARVIS sleeping...")
print("Say: HEY JARVIS")

def callback(indata, frames, time, status):
    if status:
        print(status)

    audio = indata[:, 0].astype(np.int16)

    score = float(model.predict(audio)["hey_jarvis"])

    if score > 0.01:
        print(f"score: {score:.3f}")

    if score > 0.5:
        print("\n🔥 HEY JARVIS DETECTED\n")

with sd.InputStream(
    samplerate=16000,
    blocksize=1280,
    channels=1,
    dtype="int16",
    device=0,
    callback=callback,
):
    while True:
        sd.sleep(1000)
