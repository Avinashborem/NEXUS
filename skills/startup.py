# skills/startup.py — Auto startup on Windows boot
import os, sys, winreg

NEXUS_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'main.py'))
PYTHON_PATH = sys.executable
REG_KEY     = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME    = "NEXUS"

def enable_startup():
    """Add NEXUS to Windows startup"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             REG_KEY, 0, winreg.KEY_SET_VALUE)
        cmd = f'"{PYTHON_PATH}" "{NEXUS_PATH}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        return "NEXUS will now start automatically when Windows boots."
    except Exception as e:
        return f"Could not enable startup: {e}"

def disable_startup():
    """Remove NEXUS from Windows startup"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             REG_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return "NEXUS removed from startup."
    except FileNotFoundError:
        return "NEXUS was not in startup."
    except Exception as e:
        return f"Could not disable startup: {e}"

def check_startup():
    """Check if NEXUS is set to auto-start"""
    try:
        key  = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              REG_KEY, 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return "NEXUS is set to start automatically on boot."
    except FileNotFoundError:
        return "NEXUS is not set to auto-start."
    except Exception as e:
        return f"Could not check startup: {e}"