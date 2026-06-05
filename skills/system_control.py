# skills/system_control.py — Full System Control
import os, subprocess, psutil, pyautogui, pyperclip, webbrowser, shutil, glob

def open_app(app_name):
    name = app_name.lower().strip()

    builtin = {
        "notepad":       "notepad.exe",
        "calculator":    "calc.exe",
        "paint":         "mspaint.exe",
        "vs code":       "code",
        "vscode":        "code",
        "file explorer": "explorer.exe",
        "explorer":      "explorer.exe",
        "task manager":  "taskmgr.exe",
        "cmd":           "cmd.exe",
        "command prompt":"cmd.exe",
        "word":          "winword.exe",
        "excel":         "excel.exe",
        "powerpoint":    "powerpnt.exe",
        "control panel": "control.exe",
        "registry":      "regedit.exe",
        "brave":         "brave.exe",
    }

    path_guesses = {
        "chrome":       [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
        "google chrome":[r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
        "brave":        [r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                         r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"],
        "firefox":      [r"C:\Program Files\Mozilla Firefox\firefox.exe",
                         r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"],
        "edge":         [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                         r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"],
        "spotify":      [os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe")],
        "discord":      [os.path.expanduser(r"~\AppData\Local\Discord\Update.exe")],
        "vlc":          [r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                         r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"],
        "steam":        [r"C:\Program Files (x86)\Steam\steam.exe"],
        "whatsapp":     [os.path.expanduser(r"~\AppData\Local\WhatsApp\WhatsApp.exe")],
        "telegram":     [os.path.expanduser(r"~\AppData\Roaming\Telegram Desktop\Telegram.exe")],
        "zoom":         [os.path.expanduser(r"~\AppData\Roaming\Zoom\bin\Zoom.exe")],
        "obs":          [r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"],
        "postman":      [os.path.expanduser(r"~\AppData\Local\Postman\Postman.exe")],
    }

    # 1 — builtins
    if name in builtin:
        try:
            subprocess.Popen(builtin[name], shell=True)
            return f"Opening {app_name}."
        except Exception as e:
            return f"Couldn't open {app_name}: {e}"

    # 2 — known paths
    if name in path_guesses:
        for path in path_guesses[name]:
            if os.path.exists(path):
                subprocess.Popen([path])
                return f"Opening {app_name}."
        return f"{app_name} doesn't seem to be installed, sir."

    # 3 — Start Menu shortcuts
    start_menus = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
    ]
    for base in start_menus:
        for lnk in glob.glob(os.path.join(base, "**", "*.lnk"), recursive=True):
            if name in os.path.basename(lnk).lower():
                os.startfile(lnk)
                return f"Opening {app_name}."

    # 4 — scan Program Files
    scan_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expanduser(r"~\AppData\Local"),
        os.path.expanduser(r"~\AppData\Roaming"),
    ]
    for base in scan_dirs:
        matches = glob.glob(os.path.join(base, "**", f"*{name}*.exe"), recursive=True)
        for exe in matches:
            try:
                subprocess.Popen([exe])
                return f"Opening {app_name}."
            except:
                continue

    # 5 — shutil PATH
    found = shutil.which(name) or shutil.which(app_name)
    if found:
        subprocess.Popen([found])
        return f"Opening {app_name}."

    # 6 — last resort
    try:
        subprocess.Popen(app_name, shell=True)
        return f"Attempting to open {app_name}."
    except:
        return f"I couldn't find {app_name} on this system, sir."


def open_chrome_profile(profile_name="Default"):
    from config import CHROME_PROFILES
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    profile = CHROME_PROFILES.get(profile_name.lower().strip(), profile_name)

    for path in chrome_paths:
        if os.path.exists(path):
            if profile == "Guest Profile":
                # Kill existing Chrome first, then open guest
                os.system("taskkill /f /im chrome.exe >nul 2>&1")
                import time
                time.sleep(1)
                subprocess.Popen([path, "--guest", "--new-window"])
            else:
                # Open specific profile without touching existing windows
                subprocess.Popen([
                    path,
                    f"--profile-directory={profile}",
                    "--new-window"
                ])
            return f"Opening Chrome with {profile_name} profile."
    return "Chrome not found on this system."


def get_battery():
    battery = psutil.sensors_battery()
    if battery:
        status = "charging" if battery.power_plugged else "not charging"
        return f"Battery is at {int(battery.percent)} percent and {status}."
    return "This device doesn't report battery info."


def take_screenshot():
    path = os.path.expanduser("~/Desktop/nexus_screenshot.png")
    pyautogui.screenshot(path)
    return "Screenshot saved to your Desktop."


def shutdown_pc():
    os.system("shutdown /s /t 5")
    return "Shutting down in 5 seconds."


def restart_pc():
    os.system("shutdown /r /t 5")
    return "Restarting in 5 seconds."


def get_clipboard():
    content = pyperclip.paste()
    return f"Clipboard contains: {content[:200]}" if content else "Clipboard is empty."


def open_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url}."


def get_system_info():
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')
    return (f"CPU at {cpu} percent. "
            f"RAM at {ram.percent} percent with "
            f"{round(ram.available/1024**3,1)} gigabytes free. "
            f"Disk at {disk.percent} percent.")


def set_volume(level):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices   = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume    = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level} percent."
    except:
        return "Install pycaw for precise volume control: pip install pycaw"


def type_text(text):
    import time
    time.sleep(0.5)
    pyautogui.write(text, interval=0.04)
    return f"Typed the text."


def press_key(key):
    keys = key.lower().replace("+", " ").split()
    if len(keys) > 1:
        pyautogui.hotkey(*keys)
    else:
        pyautogui.press(keys[0])
    return f"Pressed {key}."


def create_file(filename, content):
    path = os.path.expanduser(f"~/Desktop/{filename}")
    with open(path, 'w') as f:
        f.write(content)
    return f"File {filename} created on your Desktop."


def get_running_processes():
    procs = [p.name() for p in psutil.process_iter(['name'])]
    common = [p for p in procs if p.endswith('.exe')][:10]
    return "Running processes: " + ", ".join(common)


def kill_process(process_name):
    killed = False
    for proc in psutil.process_iter(['name']):
        if process_name.lower() in proc.info['name'].lower():
            proc.kill()
            killed = True
    return f"Closed {process_name}." if killed else f"Couldn't find {process_name} running."