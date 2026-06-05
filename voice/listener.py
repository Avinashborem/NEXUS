# voice/listener.py — Hybrid Google + Whisper listener
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import queue, threading
from faster_whisper import WhisperModel

print("🔄 Loading voice model...")
whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
print("✅ Voice model ready.")

recognizer = sr.Recognizer()
recognizer.energy_threshold        = 400
recognizer.dynamic_energy_threshold= True
recognizer.pause_threshold         = 0.8
recognizer.non_speaking_duration   = 0.4

# Noise phrases Whisper hallucinates
NOISE = {
    "",".","..",  "...","you","the","a","uh","um","hmm","hm",
    "i","oh","okay","ok","bye","goodbye","subscribe",
    "like and subscribe","see you next time","thanks for watching",
    "thank you for watching","thank you","thanks",
    "see you in the next video","that's it",
    "i'll see you in the next video","milk",
    "we'll take a good day",
}

def _is_noise(text):
    t = text.strip().lower().strip(".")
    if not t or len(t) < 3: return True
    if t in NOISE: return True
    # Repetition check — same phrase repeated 3+ times
    words = t.split()
    if len(words) >= 6:
        half = words[:len(words)//2]
        other= words[len(words)//2:len(words)//2+len(half)]
        if half == other: return True
    return False

def _google_listen():
    """Primary: Google Speech API — best for Indian accent"""
    try:
        with sr.Microphone() as source:
            print("🎙  Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
            text  = recognizer.recognize_google(audio).lower()
            return text
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        # Google failed — fall back to Whisper
        return _whisper_listen()
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Google error: {e}")
        return ""

def _whisper_listen():
    """Fallback: Whisper (offline)"""
    try:
        SAMPLE_RATE = 16000
        CHUNK       = 1024
        audio_queue = queue.Queue()
        frames      = []
        THRESHOLD   = 0.018

        def callback(indata, f, t, s):
            audio_queue.put(indata.copy())

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                            dtype='float32', blocksize=CHUNK,
                            callback=callback):
            started = False; timeout = 0; silence = 0

            while not started and timeout < 80:
                try:
                    chunk = audio_queue.get(timeout=0.1)
                    if np.abs(chunk).mean() > THRESHOLD:
                        started = True
                        frames.append(chunk)
                    else:
                        timeout += 1
                except queue.Empty:
                    timeout += 1

            if not started: return ""

            while silence < 20:
                try:
                    chunk = audio_queue.get(timeout=0.1)
                    frames.append(chunk)
                    if np.abs(chunk).mean() < THRESHOLD:
                        silence += 1
                    else:
                        silence = 0
                except queue.Empty:
                    break

        if len(frames) < 8: return ""

        audio_data = np.concatenate(frames, axis=0).flatten()
        segments, _ = whisper_model.transcribe(
            audio_data, language="en",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms":600,"threshold":0.5},
            no_speech_threshold=0.65,
            temperature=0.0,
            condition_on_previous_text=False,
        )
        return " ".join([s.text for s in segments]).strip().lower()
    except Exception as e:
        print(f"Whisper error: {e}")
        return ""

def listen():
    try:
        text = _google_listen()
        if not text:
            return ""
        if _is_noise(text):
            print(f"[filtered noise: {text[:40]}]")
            return ""
        print(f"You: {text}")
        return text
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Listener error: {e}")
        return ""