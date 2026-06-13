# skills/vision.py — True Live Vision Agent
import mss, cv2, numpy as np, threading, time, base64, io, os
from PIL import Image
import anthropic
from config import ANTHROPIC_API_KEY

# ── Live screen buffer ────────────────────────────────────────────
_latest_frame = None
_frame_lock   = threading.Lock()
_watching     = False

def _capture_loop():
    global _latest_frame, _watching
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while _watching:
            try:
                frame = sct.grab(monitor)
                img   = np.array(frame)
                with _frame_lock:
                    _latest_frame = img
                time.sleep(0.3)  # ~3fps live feed
            except:
                time.sleep(1)

def start_watching():
    global _watching
    if not _watching:
        _watching = True
        t = threading.Thread(target=_capture_loop, daemon=True)
        t.start()

def get_latest_frame():
    with _frame_lock:
        if _latest_frame is None:
            with mss.mss() as sct:
                frame = sct.grab(sct.monitors[1])
                return np.array(frame)
        return _latest_frame.copy()

def frame_to_base64():
    """Convert current screen to base64 for Claude vision"""
    frame  = get_latest_frame()
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img    = Image.fromarray(frame)
    # Resize to save tokens — Claude handles 1568px well
    w, h   = img.size
    if w > 1568:
        ratio = 1568/w
        img   = img.resize((1568, int(h*ratio)), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()

def frame_to_pil(frame=None):
    if frame is None:
        frame = get_latest_frame()
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame)

# ── Claude Vision — understands screen like a human ───────────────
def analyze_screen(question="What is on the screen right now?"):
    """Send live screen to Claude Vision and get intelligent answer"""
    try:
        client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        img_b64 = frame_to_base64()

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": f"{question}\n\nBe concise and direct. If asked to find something specific, give exact coordinates or location on screen."
                    }
                ]
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"Vision failed: {e}"

def read_screen():
    """NEXUS reads and understands the current screen"""
    try:
        import pygetwindow as gw
        win   = gw.getActiveWindow()
        title = win.title if win else "Unknown"
    except:
        title = "Unknown"

    analysis = analyze_screen(
        "Describe what is on this screen briefly. "
        "What app is open? What content is visible? "
        "What can the user interact with?"
    )
    return f"Active: {title}. {analysis}"

def find_element(description):
    """Find UI element on screen using Claude Vision"""
    result = analyze_screen(
        f"Find '{description}' on this screen. "
        f"Give me the approximate X,Y pixel coordinates where it is. "
        f"Format: X=<number> Y=<number>. "
        f"Screen resolution context: the screen is typically 1920x1080."
    )
    return result

def smart_click(description):
    """Find and click an element using Claude Vision"""
    import pyautogui
    import re

    # Get screen size
    sw, sh = pyautogui.size()

    # Ask Claude where to click
    result = analyze_screen(
        f"I need to click on '{description}'. "
        f"The screen resolution is {sw}x{sh}. "
        f"Give me ONLY the X and Y pixel coordinates like: X=850 Y=340. "
        f"Nothing else, just X=<number> Y=<number>."
    )

    # Parse coordinates
    x_match = re.search(r'X=(\d+)', result)
    y_match = re.search(r'Y=(\d+)', result)

    if x_match and y_match:
        x = int(x_match.group(1))
        y = int(y_match.group(1))
        # Safety bounds check
        if 0 < x < sw and 0 < y < sh:
            pyautogui.moveTo(x, y, duration=0.4)
            time.sleep(0.2)
            pyautogui.click(x, y)
            return f"Clicked '{description}' at {x},{y}."
        else:
            return f"Coordinates out of bounds: {x},{y}"
    return f"Could not locate '{description}' on screen. Claude said: {result}"

def click_on_text(text):
    """Click on visible text using vision"""
    return smart_click(text)

def double_click_on_text(text):
    import pyautogui, re
    sw, sh = pyautogui.size()
    result = analyze_screen(
        f"Find '{text}' on screen ({sw}x{sh}). "
        f"Give coordinates as X=<n> Y=<n> only."
    )
    x_match = re.search(r'X=(\d+)', result)
    y_match = re.search(r'Y=(\d+)', result)
    if x_match and y_match:
        x, y = int(x_match.group(1)), int(y_match.group(1))
        pyautogui.doubleClick(x, y)
        return f"Double-clicked '{text}'."
    return f"Could not find '{text}'."

def right_click_on_text(text):
    import pyautogui, re
    sw, sh = pyautogui.size()
    result = analyze_screen(
        f"Find '{text}' on screen ({sw}x{sh}). "
        f"Give coordinates as X=<n> Y=<n> only."
    )
    x_match = re.search(r'X=(\d+)', result)
    y_match = re.search(r'Y=(\d+)', result)
    if x_match and y_match:
        x, y = int(x_match.group(1)), int(y_match.group(1))
        pyautogui.rightClick(x, y)
        return f"Right-clicked '{text}'."
    return f"Could not find '{text}'."

def get_active_window():
    try:
        import pygetwindow as gw
        win = gw.getActiveWindow()
        return f"Active window: {win.title}" if win else "No active window."
    except:
        return "Could not get window."

def get_all_windows():
    try:
        import pygetwindow as gw
        wins = [w.title for w in gw.getAllWindows() if w.title.strip()]
        return "Open windows: " + ", ".join(wins[:10])
    except:
        return "Could not list windows."

def focus_window(title):
    try:
        import pygetwindow as gw
        wins = gw.getWindowsWithTitle(title)
        if wins:
            wins[0].activate()
            return f"Focused: {title}"
        # Try partial match
        for w in gw.getAllWindows():
            if title.lower() in w.title.lower():
                w.activate()
                return f"Focused: {w.title}"
        return f"Window not found: {title}"
    except Exception as e:
        return f"Could not focus: {e}"

def scroll(direction="down", amount=3):
    import pyautogui
    clicks = -amount if direction == "down" else amount
    pyautogui.scroll(clicks * 3)
    return f"Scrolled {direction}."

def what_can_i_do():
    """NEXUS analyzes screen and suggests what actions are possible"""
    return analyze_screen(
        "Look at this screen and tell me: "
        "what are the main things the user can do or interact with right now? "
        "Be brief, 2-3 sentences max."
    )

def play_first_youtube_result():
    """Specifically designed to click first YouTube video result"""
    import pyautogui
    return smart_click(
        "the first video thumbnail or first video title in YouTube search results"
    )

# Auto-start
start_watching()