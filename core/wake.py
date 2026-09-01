import sounddevice as sd
import numpy as np
from openwakeword.model import Model

SAMPLE_RATE = 16000
CHUNK = 1280
THRESHOLD = 0.5

_model = None


def wait_for_wake():
    global _model

    if _model is None:
        print("Loading wake detector...")
        _model = Model(wakeword_models=["hey_jarvis"])
        print("Wake detector ready.")

    print("😴 JARVIS sleeping...")
    print("Say: Hey Jarvis")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK,
    ) as stream:

        while True:
            audio, _ = stream.read(CHUNK)
            audio = np.squeeze(audio)

            scores = _model.predict(audio)
            score = float(scores.get("hey_jarvis", 0))

            if score >= THRESHOLD:
                print(f"🔥 JARVIS ACTIVATED ({score:.2f})")
                return True
