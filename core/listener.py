import time
import threading

import numpy as np
import sounddevice as sd
from openwakeword.model import Model
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_DEVICE = 0

WAKE_BLOCK_SIZE = 1280
RECORD_BLOCK_SIZE = 1024

# Lower = more sensitive microphone detection
SILENCE_THRESHOLD = 180

# Wait this long after speech stops
SILENCE_DURATION = 1.3

# Maximum length of one command
MAX_RECORD_SECONDS = 15


print("Loading wake word...")

wake_model = Model(
    wakeword_models=["hey_jarvis"]
)

print("Loading Whisper...")

whisper_model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
)

print("🟢 JARVIS listener ready.")


def wait_for_wake_word():
    print("😴 Waiting for HEY JARVIS...")

    detected = threading.Event()

    def callback(indata, frames, time_info, status):
        try:
            audio = indata[:, 0].astype(np.int16)

            prediction = wake_model.predict(audio)

            score = float(
                prediction.get("hey_jarvis", 0)
            )

            if score > 0.5:
                print(f"🔥 HEY JARVIS ({score:.2f})")
                detected.set()

        except Exception as e:
            print(f"Wake word error: {e}")

    stream = None

    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=WAKE_BLOCK_SIZE,
            channels=CHANNELS,
            dtype="int16",
            device=AUDIO_DEVICE,
            callback=callback,
        )

        stream.start()

        while not detected.is_set():
            sd.sleep(50)

    finally:
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass

            try:
                stream.close()
            except Exception:
                pass


def record_until_silence():
    print("🎙️ Listening...")

    frames = []
    started = False
    silence_start = None
    start_time = time.time()

    def callback(indata, frame_count, time_info, status):
        try:
            frames.append(indata[:, 0].copy())
        except Exception:
            pass

    stream = None

    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=RECORD_BLOCK_SIZE,
            channels=CHANNELS,
            dtype="int16",
            device=AUDIO_DEVICE,
            callback=callback,
        )

        stream.start()

        while True:
            sd.sleep(50)

            if not frames:
                continue

            recent = np.concatenate(frames[-5:])
            volume = np.abs(recent).mean()

            # User is speaking
            if volume > SILENCE_THRESHOLD:
                started = True
                silence_start = None

            # User stopped speaking
            elif started:

                if silence_start is None:
                    silence_start = time.time()

                elif (
                    time.time() - silence_start
                    > SILENCE_DURATION
                ):
                    break

            # Hard timeout
            if (
                time.time() - start_time
                > MAX_RECORD_SECONDS
            ):
                break

    finally:
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass

            try:
                stream.close()
            except Exception:
                pass

    if not frames:
        return ""

    audio = np.concatenate(
        frames
    ).astype(np.float32) / 32768.0

    try:
        segments, info = whisper_model.transcribe(
            audio,
            beam_size=5,
            language="en",
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 700,
            },
            condition_on_previous_text=False,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return ""

    print(f"📝 You: {text}")

    return text
