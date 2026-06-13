# skills/whatsapp.py — WhatsApp Control via Web/App
import subprocess, os, time, webbrowser, pyautogui
import pygetwindow as gw

WHATSAPP_EXE = os.path.expanduser(r"~\AppData\Local\WhatsApp\WhatsApp.exe")

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

def _is_running(name):
    import psutil
    return any(name.lower() in p.name().lower()
               for p in psutil.process_iter(['name']))

def send_whatsapp(contact, message):
    """Send WhatsApp message using Vision to find contact"""
    try:
        # Open WhatsApp
        if os.path.exists(WHATSAPP_EXE):
            if not _is_running("whatsapp"):
                subprocess.Popen([WHATSAPP_EXE])
                time.sleep(5)
            _focus_window("whatsapp")
        else:
            # Use WhatsApp Web
            webbrowser.open("https://web.whatsapp.com")
            time.sleep(4)
            for kw in ["whatsapp", "brave", "chrome"]:
                if _focus_window(kw): break

        time.sleep(1)

        # Search for contact
        try:
            from skills.vision import smart_click
            smart_click("search bar or search contacts input")
        except:
            pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)

        pyautogui.write(contact, interval=0.05)
        time.sleep(1.5)

        # Click the contact from results
        try:
            from skills.vision import smart_click
            smart_click(f"{contact} in the contacts list")
        except:
            pyautogui.press('enter')
        time.sleep(1)

        # Click message input and type
        try:
            from skills.vision import smart_click
            smart_click("message input box at the bottom")
        except:
            pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

        pyautogui.write(message, interval=0.04)
        time.sleep(0.3)
        pyautogui.press('enter')
        return f"Message sent to {contact}: {message}"

    except Exception as e:
        return f"WhatsApp failed: {e}"

def open_whatsapp_chat(contact):
    """Just open a chat without sending"""
    try:
        if os.path.exists(WHATSAPP_EXE):
            if not _is_running("whatsapp"):
                subprocess.Popen([WHATSAPP_EXE])
                time.sleep(5)
            _focus_window("whatsapp")
        else:
            webbrowser.open("https://web.whatsapp.com")
            time.sleep(4)
            for kw in ["whatsapp", "brave", "chrome"]:
                if _focus_window(kw): break

        time.sleep(1)

        try:
            from skills.vision import smart_click
            smart_click("search bar or search contacts input")
        except:
            pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)

        pyautogui.write(contact, interval=0.05)
        time.sleep(1.5)

        try:
            from skills.vision import smart_click
            smart_click(f"{contact} in contacts list")
        except:
            pyautogui.press('enter')

        return f"Opened WhatsApp chat with {contact}."
    except Exception as e:
        return f"Failed to open chat: {e}"

def read_whatsapp_messages(contact=None):
    """Read latest messages using screen vision"""
    try:
        if not _is_running("whatsapp"):
            return "WhatsApp is not open. Say 'open WhatsApp' first."

        _focus_window("whatsapp")
        time.sleep(0.5)

        from skills.vision import analyze_screen
        if contact:
            result = analyze_screen(
                f"What are the latest messages in the {contact} WhatsApp chat? "
                f"Read the last 3 messages and who sent them.")
        else:
            result = analyze_screen(
                "What WhatsApp chats are visible? "
                "List the names and latest message preview for top 5 chats.")
        return result
    except Exception as e:
        return f"Could not read messages: {e}"