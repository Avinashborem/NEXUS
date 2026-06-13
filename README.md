<div align="center">

# ⬡ N.E.X.U.S
### Neural Executive Unified System

**A fully autonomous AI assistant inspired by JARVIS from Iron Man**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-lightblue?style=for-the-badge&logo=windows)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

*"NEXUS online. All systems ready, sir."*

</div>

---

## 🎯 What is NEXUS?

NEXUS is a voice-controlled autonomous AI agent that runs on your Windows PC. Unlike simple voice assistants, NEXUS can **see your screen**, **control any application**, **read your emails**, **manage files**, **play music**, and hold **natural conversations** — all by voice.

Built from scratch in Python, powered by LLaMA 3.3 via Groq API, with a cinematic Iron Man-style HUD.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| 🎙 **Voice** | Whisper AI + Google Speech, noise filtering, natural conversation |
| 🧠 **AI Brain** | LLaMA 3.3-70B via Groq, tool calling, persistent memory |
| 🖥 **System Control** | Open/close apps, screenshots, processes, keyboard/mouse |
| 👁 **Screen Vision** | Real-time screen reading via OCR, click on anything visible |
| 📧 **Email** | Read, send Gmail by voice |
| 🎵 **Music** | Spotify app control, YouTube playback |
| 📁 **File Manager** | List, open, move, delete, read PDFs |
| ⏰ **Productivity** | Alarms, timers, web search, weather |
| 🌐 **Browser** | Open Chrome with specific profiles, navigate websites |
| 💾 **Memory** | Remembers conversations and user facts across sessions |
| 🎨 **HUD** | Animated fullscreen Iron Man-style interface |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│              🎙 VOICE INPUT LAYER                   │
│     faster-whisper (base.en) + Google Speech        │
│         Noise filter + VAD + Hallucination filter   │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              🧠 AI BRAIN (Groq + LLaMA 3.3)         │
│   Tool Calling → Intent → Memory → Response         │
│         SQLite persistent conversation memory       │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              ⚡ SKILL ROUTER                         │
│  System │ Vision │ Email │ Music │ Files │ Web      │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              🔊 OUTPUT LAYER                         │
│         pyttsx3 TTS + Animated HUD (tkinter)        │
└─────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

```
Language      Python 3.11
AI Model      LLaMA 3.3-70B-Versatile (Groq API — free tier)
STT           faster-whisper (base.en) + SpeechRecognition
TTS           pyttsx3
Vision        mss + OpenCV + Tesseract OCR
Memory        SQLite3
GUI/HUD       tkinter (custom animated)
Email         Gmail API (OAuth2)
Browser       selenium / webbrowser
System        psutil + pyautogui + pygetwindow
Music         Spotify app control + YouTube
```

---

## 📁 Project Structure

```
NEXUS/
├── main.py                  # Entry point
├── config.py                # API keys & settings
├── nexus_memory.db          # SQLite conversation memory
│
├── core/
│   ├── brain.py             # AI brain — LLM + tool calling
│   ├── memory.py            # Persistent memory system
│   └── intent_router.py     # Routes to brain
│
├── voice/
│   ├── listener.py          # Whisper + Google hybrid STT
│   └── stt.py               # Speech recognition utils
│
├── skills/
│   ├── system_control.py    # App launcher, processes, keyboard
│   ├── vision.py            # Screen reading + click automation
│   ├── email_skill.py       # Gmail read/send
│   ├── music.py             # Spotify + YouTube control
│   ├── file_manager.py      # File operations + PDF reading
│   ├── web_search.py        # DuckDuckGo search
│   ├── weather.py           # OpenWeatherMap
│   └── alarm.py             # Alarms + timers
│
└── output/
    ├── tts.py               # Text to speech
    └── gui.py               # Animated HUD
```

---

## 🚀 Setup

### Prerequisites
- Windows 10/11
- Python 3.11+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/NEXUS.git
cd NEXUS
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
Create `config.py`:
```python
GROQ_API_KEY     = "your_groq_api_key"       # https://console.groq.com
OPENWEATHER_KEY  = "your_openweather_key"    # https://openweathermap.org
NEXUS_NAME       = "Nexus"
WAKE_WORD        = "nexus"
CITY             = "Your City"
CONTACTS         = {
    "name": "email@gmail.com",
}
```

### 5. Gmail Setup (optional)
- Enable Gmail API at [Google Cloud Console](https://console.cloud.google.com)
- Download `credentials.json` → place in project root

### 6. Run NEXUS
```bash
python main.py
```

---

## 🎤 Voice Commands

```
"nexus, what time is it"
"open chrome personal"
"check my emails"
"play Believer by Imagine Dragons"
"what's on my screen"
"search for latest AI news"
"what's the weather today"
"set alarm for 7 AM"
"how is my system doing"
"open downloads folder"
"read my latest email"
"send email to Bittu saying I'll be late"
"take a screenshot"
"scroll down"
"close this window"
```

---

## 📦 Requirements

```
faster-whisper
SpeechRecognition
pyaudio
sounddevice
pyttsx3
groq
requests
psutil
pyautogui
pygetwindow
duckduckgo-search
schedule
plyer
pyperclip
pillow
customtkinter
mss
opencv-python
pytesseract
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
PyPDF2
spotipy
pygame
```

---

## 🗺 Roadmap

- [x] Voice input + AI conversation
- [x] System control (apps, processes, keyboard)
- [x] Screen vision + click automation
- [x] Gmail integration
- [x] Music control (Spotify + YouTube)
- [x] File management + PDF reading
- [x] Persistent memory
- [x] Animated HUD
- [ ] WhatsApp messaging
- [ ] Calendar + schedule management
- [ ] Auto-startup on boot
- [ ] Proactive alerts
- [ ] Full autonomous computer agent

---

## 👤 Author

**Avinash Borem**
CSE Final Year Student
[GitHub](https://github.com/YOUR_USERNAME) · [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

---

<div align="center">

*Built with 🔥 — because why have a basic assistant when you can have JARVIS?*

</div>
