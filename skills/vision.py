# skills/vision.py — NEXUS Continuous Screen Vision
import mss, cv2, numpy as np, threading, time, base64, io, os
from PIL import Image

# ── Live screen buffer — always holds latest frame ────────────────
_latest_frame  = None
_frame_lock    = threading.Lock()
_watching      = False
_watch_thread  = None

def _capture_loop():
    """Runs in background — continuously captures screen"""
    global _latest_frame, _watching
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary screen
        while _watching:
            try:
                frame = sct.grab(monitor)
                img   = np.array(frame)
                img   = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                with _frame_lock:
                    _latest_frame = img
                time.sleep(0.5)  # 2fps — low CPU, always fresh
            except Exception as e:
                time.sleep(1)

def start_watching():
    """Start continuous screen monitoring"""
    global _watching, _watch_thread
    if _watching:
        return "Already watching screen."
    _watching     = True
    _watch_thread = threading.Thread(target=_capture_loop, daemon=True)
    _watch_thread.start()
    return "Screen monitoring active."

def stop_watching():
    global _watching
    _watching = False
    return "Screen monitoring stopped."

def get_latest_frame():
    """Get the most recent screen frame"""
    with _frame_lock:
        if _latest_frame is None:
            # Capture once if not watching
            with mss.mss() as sct:
                monitor  = sct.monitors[1]
                frame    = sct.grab(monitor)
                return np.array(frame)
        return _latest_frame.copy()

def frame_to_pil(frame):
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame)

def frame_to_base64(frame=None):
    if frame is None:
        frame = get_latest_frame()
    img    = frame_to_pil(frame)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# ── OCR — read text from screen ───────────────────────────────────
def read_screen_text(region=None):
    """Extract all text from current screen using OCR"""
    try:
        import pytesseract
        # Try common Tesseract paths
        for path in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

        frame = get_latest_frame()
        img   = frame_to_pil(frame)

        if region:
            img = img.crop(region)  # (left, top, right, bottom)

        text = pytesseract.image_to_string(img, config='--psm 6')
        text = text.strip()
        return text[:1000] if text else "No text detected on screen."
    except Exception as e:
        return f"OCR failed: {e}. Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki"

def read_screen():
    """What NEXUS sees right now — text + active window"""
    try:
        import pygetwindow as gw
        win   = gw.getActiveWindow()
        title = win.title if win else "Unknown"
    except:
        title = "Unknown"

    text = read_screen_text()
    return f"Active window: {title}. Screen content: {text[:400]}"

# ── Find & interact with screen elements ─────────────────────────
def find_text_location(search_text):
    """Find exact pixel location of text on screen"""
    try:
        import pytesseract
        for path in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

        frame = get_latest_frame()
        img   = frame_to_pil(frame)
        data  = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        results = []
        for i, word in enumerate(data['text']):
            if (search_text.lower() in word.lower()
                    and int(data['conf'][i]) > 50):
                x = data['left'][i] + data['width'][i]//2
                y = data['top'][i] + data['height'][i]//2
                results.append((x, y, word, data['conf'][i]))

        return results
    except Exception as e:
        return []

def click_on_text(text):
    """Find text on screen and click it"""
    import pyautogui, time
    results = find_text_location(text)
    if results:
        x, y, word, conf = results[0]
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.1)
        pyautogui.click(x, y)
        return f"Clicked '{word}' at {x},{y}."
    return f"Could not find '{text}' on screen."

def move_mouse_to_text(text):
    """Move mouse to text without clicking"""
    import pyautogui
    results = find_text_location(text)
    if results:
        x, y, word, _ = results[0]
        pyautogui.moveTo(x, y, duration=0.4)
        return f"Mouse moved to '{word}'."
    return f"Could not find '{text}'."

def double_click_on_text(text):
    import pyautogui, time
    results = find_text_location(text)
    if results:
        x, y, word, _ = results[0]
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.1)
        pyautogui.doubleClick(x, y)
        return f"Double-clicked '{word}'."
    return f"Could not find '{text}'."

def right_click_on_text(text):
    import pyautogui, time
    results = find_text_location(text)
    if results:
        x, y, word, _ = results[0]
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.1)
        pyautogui.rightClick(x, y)
        return f"Right-clicked '{word}'."
    return f"Could not find '{text}'."

def click_at(x, y):
    import pyautogui
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click(x, y)
    return f"Clicked at {x},{y}."

def drag_from_to(x1, y1, x2, y2):
    import pyautogui
    pyautogui.moveTo(x1, y1, duration=0.3)
    pyautogui.dragTo(x2, y2, duration=0.5, button='left')
    return f"Dragged from {x1},{y1} to {x2},{y2}."

def scroll(direction="down", amount=3):
    import pyautogui
    clicks = -amount if direction=="down" else amount
    pyautogui.scroll(clicks * 3)
    return f"Scrolled {direction}."

def get_active_window():
    try:
        import pygetwindow as gw
        win = gw.getActiveWindow()
        return f"Active window: {win.title}" if win else "No active window."
    except:
        return "Could not get active window."

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
            return f"Focused window: {title}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Could not focus window: {e}"

def save_screenshot(filename="nexus_screen.png"):
    frame = get_latest_frame()
    path  = os.path.expanduser(f"~/Desktop/{filename}")
    img   = frame_to_pil(frame)
    img.save(path)
    return f"Screenshot saved to Desktop as {filename}."

# Auto-start watching when imported
start_watching()