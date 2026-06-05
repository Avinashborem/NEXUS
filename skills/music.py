# skills/music.py — Full Music Agent v2
import subprocess, os, time, webbrowser, pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False

SPOTIFY_EXE = os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe")

def _is_running(name):
    import psutil
    return any(name.lower() in p.name().lower()
               for p in psutil.process_iter(['name']))

def _focus_window(keyword):
    """Bring window with keyword in title to front"""
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
        # Launch Spotify if not running
        if not _is_running("spotify"):
            if os.path.exists(SPOTIFY_EXE):
                subprocess.Popen([SPOTIFY_EXE])
                time.sleep(5)  # wait for startup
            else:
                return play_youtube(query)

        # Focus Spotify window
        if not _focus_window("spotify"):
            time.sleep(2)
            _focus_window("spotify")

        time.sleep(0.5)

        # Open search with Ctrl+L (Spotify shortcut)
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.6)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(query, interval=0.05)
        time.sleep(0.4)
        pyautogui.press('enter')
        time.sleep(2.5)  # wait for results

        # Press Tab to navigate to first song result and Enter to play
        # Spotify layout: after search, Tab moves through results
        for _ in range(4):
            pyautogui.press('tab')
            time.sleep(0.15)
        pyautogui.press('enter')
        time.sleep(0.5)

        return f"Playing {query} on Spotify."
    except Exception as e:
        return f"Spotify failed: {e}. Trying YouTube."

# ── YOUTUBE — open AND click first video ─────────────────────────
def play_youtube(query):
    try:
        # Open YouTube search
        url = f"https://www.youtube.com/results?search_query={query.replace(' ','+')}"
        webbrowser.open(url)
        time.sleep(3.5)  # wait for page load

        # Focus browser
        for kw in ["youtube", "brave", "chrome", "firefox", "edge"]:
            if _focus_window(kw):
                break
        time.sleep(0.5)

        # Click directly on first video thumbnail
        # YouTube first video result is consistently at around these positions
        # Use Tab navigation which is more reliable
        pyautogui.hotkey('ctrl', 'l')  # focus address bar
        time.sleep(0.3)
        # Tab out of address bar into page content
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)

        # Now use vision to find and click first video
        from skills.vision import get_latest_frame, frame_to_pil
        import pytesseract, numpy as np

        # Try OCR approach — find video titles on screen
        try:
            frame = get_latest_frame()
            img   = frame_to_pil(frame)

            # Click on the first video thumbnail area
            # YouTube search results first video thumbnail is typically
            # in the main content area — use pyautogui to click it
            sw, sh = pyautogui.size()

            # First video thumbnail is roughly at 55% width, 30% height
            # This is consistent across YouTube layouts
            click_x = int(sw * 0.50)
            click_y = int(sh * 0.38)
            pyautogui.moveTo(click_x, click_y, duration=0.3)
            time.sleep(0.2)
            pyautogui.click(click_x, click_y)
            time.sleep(1)

            # If that didn't work, try clicking the title text area
            # which is to the right of thumbnail
            click_x2 = int(sw * 0.72)
            click_y2 = int(sh * 0.28)
            pyautogui.moveTo(click_x2, click_y2, duration=0.3)
            time.sleep(0.2)
            pyautogui.click(click_x2, click_y2)

        except Exception:
            # Pure fallback — just click center-ish of first result
            sw, sh = pyautogui.size()
            pyautogui.click(int(sw*0.5), int(sh*0.35))

        return f"Playing {query} on YouTube."
    except Exception as e:
        return f"YouTube failed: {e}"

def play_music(query, platform="auto"):
    """Smart router — Spotify if installed, else YouTube"""
    p = platform.lower()
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
    # Try Spotify shortcut first, then media key
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
    for _ in range(steps):
        pyautogui.press('volumeup')
    return "Volume up."

def volume_down(steps=5):
    for _ in range(steps):
        pyautogui.press('volumedown')
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
    return "Music stopped."