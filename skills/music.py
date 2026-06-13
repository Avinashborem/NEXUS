# skills/music.py — Full Music Agent v3
import subprocess, os, time, webbrowser, pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False

SPOTIFY_EXE = os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe")

def _is_running(name):
    import psutil
    return any(name.lower() in p.name().lower()
               for p in psutil.process_iter(['name']))

def _focus_window(keyword):
    try:
        wins = [w for w in gw.getAllWindows()
                if keyword.lower() in w.title.lower() and w.title.strip()]
        if wins:
            wins[0].activate()
            time.sleep(0.5)
            return True
    except: pass
    return False

# ── SPOTIFY ───────────────────────────────────────────────────────
def play_spotify(query):
    try:
        # Launch if not running
        if not _is_running("spotify"):
            if os.path.exists(SPOTIFY_EXE):
                subprocess.Popen([SPOTIFY_EXE])
                time.sleep(5)
            else:
                return "Spotify is not installed. Try YouTube instead."

        # Focus Spotify
        if not _focus_window("spotify"):
            time.sleep(2)
            _focus_window("spotify")
        time.sleep(0.5)

        # Search
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.6)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(query, interval=0.05)
        time.sleep(0.4)
        pyautogui.press('enter')
        time.sleep(2.5)

        # Use Claude Vision to click first song
        try:
            from skills.vision import smart_click
            smart_click("first song result in the list, not a playlist or album")
        except:
            # Fallback tab navigation
            for _ in range(4):
                pyautogui.press('tab')
                time.sleep(0.15)
            pyautogui.press('enter')

        time.sleep(0.5)
        return f"Playing {query} on Spotify."
    except Exception as e:
        return f"Spotify failed: {e}"

# ── YOUTUBE ───────────────────────────────────────────────────────
def play_youtube(query):
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ','+')}"
        webbrowser.open(url)
        time.sleep(4)

        for kw in ["youtube", "brave", "chrome", "firefox", "edge"]:
            if _focus_window(kw):
                break
        time.sleep(1)

        # Use Claude Vision to click first video
        try:
            from skills.vision import smart_click
            smart_click("first video thumbnail or first video title in YouTube search results")
        except:
            # Fallback — click at typical first result position
            sw, sh = pyautogui.size()
            pyautogui.click(int(sw * 0.50), int(sh * 0.35))

        time.sleep(1)
        return f"Playing {query} on YouTube."
    except Exception as e:
        return f"YouTube failed: {e}"

# ── SMART ROUTER ──────────────────────────────────────────────────
def play_music(query, platform="auto"):
    """
    platform = auto   → Spotify if installed, else YouTube
    platform = spotify → force Spotify
    platform = youtube → force YouTube
    """
    p = platform.lower().strip()

    if p == "spotify":
        return play_spotify(query)
    elif p == "youtube":
        return play_youtube(query)
    else:
        # Auto — prefer Spotify app if installed
        if os.path.exists(SPOTIFY_EXE):
            return play_spotify(query)
        return play_youtube(query)

# ── CONTROLS ──────────────────────────────────────────────────────
def pause_resume():
    if _is_running("spotify") and _focus_window("spotify"):
        pyautogui.press('space')
    else:
        pyautogui.press('playpause')
    return "Toggled play/pause."

def next_track():
    if _is_running("spotify") and _focus_window("spotify"):
        pyautogui.hotkey('ctrl', 'right')
    else:
        pyautogui.press('nexttrack')
    return "Next track."

def prev_track():
    if _is_running("spotify") and _focus_window("spotify"):
        pyautogui.hotkey('ctrl', 'left')
    else:
        pyautogui.press('prevtrack')
    return "Previous track."

def volume_up(steps=5):
    for _ in range(steps): pyautogui.press('volumeup')
    return "Volume up."

def volume_down(steps=5):
    for _ in range(steps): pyautogui.press('volumedown')
    return "Volume down."

def mute():
    pyautogui.press('volumemute')
    return "Toggled mute."

def stop_music():
    if _is_running("spotify"):
        import psutil
        for p in psutil.process_iter(['name']):
            if 'spotify' in p.name().lower():
                p.kill()
        return "Spotify closed."
    pyautogui.press('stop')
    return "Stopped."