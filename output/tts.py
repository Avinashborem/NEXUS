# output/tts.py — Voice Output
import pyttsx3
import re

engine = pyttsx3.init()

def setup_voice():
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 165)
    engine.setProperty('volume', 1.0)

def clean_text(text):
    # Remove any leaked function call tags
    text = re.sub(r'<function=.*?</function>', '', text)
    text = re.sub(r'<function=.*?}>', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def speak(text):
    text = clean_text(text)
    if not text:
        return
    print(f"\nNEXUS: {text}\n")
    engine.say(text)
    engine.runAndWait()

setup_voice()