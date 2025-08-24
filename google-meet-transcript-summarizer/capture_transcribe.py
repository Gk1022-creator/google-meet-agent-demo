# capture_transcribe.py
import sounddevice as sd
import numpy as np
import queue, threading, time, os, wave
from scipy.signal import resample_poly
from faster_whisper import WhisperModel

TARGET_SR = 16000
CHUNK_SEC = 5.0
MODEL_SIZE = "medium"
DEVICE_NAME_SUBSTR = "CABLE Output (VB-Audio"

q = queue.Queue(maxsize=2000)

# --- Paths for saving meeting audio + transcript ---
os.makedirs("meeting_logs", exist_ok=True)
MEETING_ID = time.strftime("%Y%m%d_%H%M%S")
AUDIO_PATH = f"meeting_logs/{MEETING_ID}.wav"
TRANSCRIPT_PATH = f"meeting_logs/{MEETING_ID}.txt"

# --- WAV writer setup ---
wav_file = wave.open(AUDIO_PATH, "wb")
wav_file.setnchannels(1)
wav_file.setsampwidth(2)       # 16-bit PCM
wav_file.setframerate(TARGET_SR)

# --- Device finder ---
def find_device(name_substr):
    devs = sd.query_devices()
    for i, d in enumerate(devs):
        if name_substr in d["name"]:
            return i, int(d["default_samplerate"])
    raise RuntimeError("Audio device not found. Check VB-Audio and app routing.")

# --- Audio callback ---
def callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)
    q.put(indata.copy())
    # save raw audio into WAV file
    wav_file.writeframes((indata * 32767).astype(np.int16).tobytes())

# --- Capture mic loop ---
def capture_loop():
    dev_idx, dev_sr = find_device(DEVICE_NAME_SUBSTR)
    print("Using device idx", dev_idx, "rate", dev_sr)
    with sd.InputStream(device=dev_idx, channels=1, dtype='float32', callback=callback, samplerate=TARGET_SR):
        while True:
            time.sleep(1)

# --- Transcribe loop ---
def transcribe_loop():
    model = WhisperModel(MODEL_SIZE, device="cpu")
    buffer = np.zeros(0, dtype=np.float32)

    while True:
        data = q.get().flatten()
        buffer = np.concatenate((buffer, data))
        if buffer.shape[0] >= int(TARGET_SR * CHUNK_SEC):
            chunk = buffer[:int(TARGET_SR * CHUNK_SEC)]
            buffer = buffer[int(TARGET_SR * CHUNK_SEC):]

            segments, _ = model.transcribe(chunk, language="en", vad_filter=True, temperature=0.0)
            text = " ".join([s.text for s in segments]).strip()
            if text:
                ts = time.strftime("%H:%M:%S")
                line = f"[{ts}] {text}"
                print(line)

                # append to transcript file
                with open(TRANSCRIPT_PATH, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

# --- Main entry ---
if __name__ == "__main__":
    t1 = threading.Thread(target=capture_loop, daemon=True); t1.start()
    t2 = threading.Thread(target=transcribe_loop, daemon=True); t2.start()
    t1.join(); t2.join()

    # close wav file when finished
    wav_file.close()
