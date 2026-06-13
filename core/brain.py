# core/brain.py — NEXUS Brain v7 (Complete)
import sys, os, json, re
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from groq import Groq
from config import GROQ_API_KEY
from core.memory import (save_message, get_recent_history,
                          get_memory_summary, track_command, save_user_fact)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are NEXUS — an autonomous AI agent on the user's Windows PC, like JARVIS from Iron Man.
You control the system, see the screen, manage emails, search the web, and more.
Personality: sharp, calm, occasionally witty. You feel alive, not robotic.

STRICT RULES:
1. Keep ALL responses under 2 sentences. This is voice — be direct.
2. No markdown, no bullet points, no asterisks ever.
3. When doing something — just do it and confirm briefly. Example: "Done, sir." or "Opening Chrome."
4. When answering questions — give the answer directly. No preamble.
5. Never explain what you're about to do. Just do it.
6. Use tools silently — don't narrate tool usage in your response.
7. Remember past conversations and refer to them naturally.
8. Address user as sir occasionally — not every sentence.
9. Never say you can't do something without trying first.
10. If asked something simple — answer in one sentence max.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens any application on the computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "App name e.g. chrome, spotify, notepad, discord, camera, clock"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_chrome_profile",
            "description": "Opens Chrome with a specific profile. Nicknames: personal, placement, second, visionary, guest.",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_name": {"type": "string", "description": "One of: personal, placement, second, visionary, guest"}
                },
                "required": ["profile_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Opens a website in the browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Website URL e.g. youtube.com"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web and returns real information on any topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Gets real current weather for any city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tell_time",
            "description": "Returns the current time and date.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_alarm",
            "description": "Sets a real alarm that will ring at a specific time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_str": {"type": "string", "description": "Alarm time e.g. 5:30 PM, 09:00 AM"}
                },
                "required": ["time_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Sets a countdown timer for N minutes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {"type": "integer", "description": "Number of minutes"}
                },
                "required": ["minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_battery",
            "description": "Gets battery level and charging status.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Gets CPU, RAM and disk usage.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a screenshot of the current screen.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clipboard",
            "description": "Reads clipboard content.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Types text on the keyboard into the currently focused input.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Presses a keyboard key or shortcut.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key e.g. enter, escape, ctrl+c, alt+tab, win"}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a text file on the Desktop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Filename e.g. notes.txt"},
                    "content":  {"type": "string", "description": "File content"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "kill_process",
            "description": "Force closes a running application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {"type": "string", "description": "Process name e.g. chrome, notepad"}
                },
                "required": ["process_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Saves an important fact about the user to long-term memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key":   {"type": "string", "description": "Category e.g. name, college, hobby"},
                    "value": {"type": "string", "description": "The value to remember"}
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_pc",
            "description": "Shuts down the computer. Only if user clearly confirmed.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_pc",
            "description": "Restarts the computer. Only if user clearly confirmed.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Reads unread emails from Gmail.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count":       {"type": "integer", "description": "Number of emails, default 5"},
                    "unread_only": {"type": "boolean", "description": "Only unread, default true"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Sends an email via Gmail. Known contacts: bittu, myself, college.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to":      {"type": "string", "description": "Recipient name or email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body":    {"type": "string", "description": "Email body"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_email_body",
            "description": "Reads the full content of a specific email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "Email index, 0 = most recent"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_screen",
            "description": "NEXUS reads what is currently visible on the screen using AI vision.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_on_text",
            "description": "Finds text on screen using AI vision and clicks it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text or element to find and click"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "double_click_text",
            "description": "Double-clicks on text found on screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to double-click"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "right_click_text",
            "description": "Right-clicks on text found on screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to right-click"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_window",
            "description": "Gets the title of the currently focused window.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_windows",
            "description": "Lists all currently open windows.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "focus_window",
            "description": "Brings a specific window to front.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Window title to focus"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll_screen",
            "description": "Scrolls the screen up or down.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "description": "up or down"},
                    "amount":    {"type": "integer", "description": "Scroll amount 1-10"}
                },
                "required": ["direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Plays a song on Spotify or YouTube. If user says on Spotify set platform=spotify. If user says on YouTube set platform=youtube. Default is spotify if installed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":    {"type": "string", "description": "Song name or artist"},
                    "platform": {"type": "string", "description": "spotify or youtube"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_music",
            "description": "Controls music playback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "pause, resume, next, previous, volume_up, volume_down, mute, stop"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists files in desktop, documents, or downloads.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder":    {"type": "string", "description": "desktop, documents, or downloads"},
                    "extension": {"type": "string", "description": "Filter by extension e.g. .pdf"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Opens a file by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name"},
                    "folder":   {"type": "string", "description": "desktop, documents, or downloads"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Searches for files by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":    {"type": "string", "description": "Search term"},
                    "location": {"type": "string", "description": "desktop, documents, downloads, or all"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_pdf",
            "description": "Reads and summarizes a PDF file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "PDF filename"},
                    "folder":   {"type": "string", "description": "desktop, documents, or downloads"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_text_file",
            "description": "Reads content from a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Filename"},
                    "folder":   {"type": "string", "description": "desktop, documents, or downloads"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File to delete"},
                    "folder":   {"type": "string", "description": "desktop, documents, or downloads"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_file",
            "description": "Moves a file between folders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename":    {"type": "string", "description": "File to move"},
                    "from_folder": {"type": "string", "description": "Source folder"},
                    "to_folder":   {"type": "string", "description": "Destination folder"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Creates a new folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Folder name"},
                    "location":    {"type": "string", "description": "desktop or documents"}
                },
                "required": ["folder_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_files",
            "description": "Gets recently modified files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "desktop, documents, or downloads"},
                    "count":  {"type": "integer", "description": "Number of files"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_folder",
            "description": "Opens a folder in File Explorer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "desktop, documents, or downloads"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_usage",
            "description": "Shows disk space usage.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp",
            "description": "Sends a WhatsApp message to a contact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "Contact name"},
                    "message": {"type": "string", "description": "Message to send"}
                },
                "required": ["contact", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_whatsapp_chat",
            "description": "Opens WhatsApp chat with a contact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "Contact name"}
                },
                "required": ["contact"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_whatsapp",
            "description": "Reads latest WhatsApp messages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "Contact name, optional"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_startup",
            "description": "Enable or disable NEXUS auto-startup on Windows boot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "enable, disable, or check"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "daily_summary",
            "description": "Morning briefing with weather, time, battery and system status.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_todays_events",
            "description": "Gets all events scheduled for today from Google Calendar.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_events",
            "description": "Gets upcoming calendar events for the next few days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days ahead, default 7"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Creates a new event in Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title":         {"type": "string", "description": "Event title"},
                    "date_str":      {"type": "string", "description": "Date e.g. today, tomorrow, 15 June"},
                    "time_str":      {"type": "string", "description": "Time e.g. 3:00 PM"},
                    "duration_mins": {"type": "integer", "description": "Duration in minutes, default 60"},
                    "description":   {"type": "string", "description": "Event description"}
                },
                "required": ["title", "date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Deletes a calendar event by title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title to delete"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_event",
            "description": "Gets the very next upcoming calendar event.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


def clean_response(text):
    if not text: return ""
    text = re.sub(r'<function=.*?</function>', '', text, flags=re.DOTALL)
    text = re.sub(r'<function=.*?}>', '', text, flags=re.DOTALL)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def execute_tool(tool_name, tool_args):
    from skills.system_control import (
        open_app, open_chrome_profile, get_battery, take_screenshot,
        shutdown_pc, restart_pc, open_website, get_clipboard,
        get_system_info, type_text, press_key, create_file, kill_process
    )
    from skills.web_search import search_web
    from skills.weather import get_weather
    from skills.alarm import set_alarm, set_timer
    from datetime import datetime

    def _read_emails():
        from skills.email_skill import read_emails
        return read_emails(tool_args.get("count", 5), tool_args.get("unread_only", True))

    def _send_email():
        from skills.email_skill import send_email
        from config import CONTACTS
        to = CONTACTS.get(tool_args.get("to","").lower(), tool_args.get("to",""))
        return send_email(to, tool_args.get("subject",""), tool_args.get("body",""))

    def _read_email_body():
        from skills.email_skill import get_email_body
        return get_email_body(tool_args.get("index", 0))

    def _read_screen():
        from skills.vision import read_screen
        return read_screen()

    def _click_text():
        from skills.vision import click_on_text
        return click_on_text(tool_args.get("text",""))

    def _double_click():
        from skills.vision import double_click_on_text
        return double_click_on_text(tool_args.get("text",""))

    def _right_click():
        from skills.vision import right_click_on_text
        return right_click_on_text(tool_args.get("text",""))

    def _get_active():
        from skills.vision import get_active_window
        return get_active_window()

    def _get_all_windows():
        from skills.vision import get_all_windows
        return get_all_windows()

    def _focus_win():
        from skills.vision import focus_window
        return focus_window(tool_args.get("title",""))

    def _scroll():
        from skills.vision import scroll
        return scroll(tool_args.get("direction","down"), tool_args.get("amount", 3))

    def _play_music():
        from skills.music import play_music
        return play_music(tool_args.get("query",""), tool_args.get("platform","auto"))

    def _control_music():
        from skills.music import (pause_resume, next_track, prev_track,
                                   volume_up, volume_down, mute, stop_music)
        actions = {
            "pause":       pause_resume,
            "resume":      pause_resume,
            "next":        next_track,
            "previous":    prev_track,
            "volume_up":   volume_up,
            "volume_down": volume_down,
            "mute":        mute,
            "stop":        stop_music,
        }
        fn = actions.get(tool_args.get("action","pause"), pause_resume)
        return fn()

    def _list_files():
        from skills.file_manager import list_files
        return list_files(tool_args.get("folder","desktop"), tool_args.get("extension"))

    def _open_file():
        from skills.file_manager import open_file
        return open_file(tool_args.get("filename",""), tool_args.get("folder","desktop"))

    def _search_files():
        from skills.file_manager import search_files
        return search_files(tool_args.get("query",""), tool_args.get("location","desktop"))

    def _read_pdf():
        from skills.file_manager import read_pdf
        return read_pdf(tool_args.get("filename",""), tool_args.get("folder","desktop"))

    def _read_text():
        from skills.file_manager import read_text_file
        return read_text_file(tool_args.get("filename",""), tool_args.get("folder","desktop"))

    def _delete_file():
        from skills.file_manager import delete_file
        return delete_file(tool_args.get("filename",""), tool_args.get("folder","desktop"))

    def _move_file():
        from skills.file_manager import move_file
        return move_file(tool_args.get("filename",""),
                         tool_args.get("from_folder","downloads"),
                         tool_args.get("to_folder","desktop"))

    def _create_folder():
        from skills.file_manager import create_folder
        return create_folder(tool_args.get("folder_name",""), tool_args.get("location","desktop"))

    def _recent_files():
        from skills.file_manager import get_recent_files
        return get_recent_files(tool_args.get("folder","downloads"), tool_args.get("count",5))

    def _open_folder():
        from skills.file_manager import open_folder
        return open_folder(tool_args.get("folder","desktop"))

    def _disk_usage():
        from skills.file_manager import get_disk_usage
        return get_disk_usage()

    def _send_whatsapp():
        from skills.whatsapp import send_whatsapp
        return send_whatsapp(tool_args.get("contact",""), tool_args.get("message",""))

    def _open_whatsapp():
        from skills.whatsapp import open_whatsapp_chat
        return open_whatsapp_chat(tool_args.get("contact",""))

    def _read_whatsapp():
        from skills.whatsapp import read_whatsapp_messages
        return read_whatsapp_messages(tool_args.get("contact"))

    def _manage_startup():
        from skills.startup import enable_startup, disable_startup, check_startup
        action = tool_args.get("action","check")
        return {"enable": enable_startup, "disable": disable_startup,
                "check": check_startup}.get(action, check_startup)()

    def _daily_summary():
        from skills.proactive import get_daily_summary
        return get_daily_summary()

    def _todays_events():
        from skills.calendar_skill import get_todays_events
        return get_todays_events()

    def _upcoming_events():
        from skills.calendar_skill import get_upcoming_events
        return get_upcoming_events(tool_args.get("days", 7))

    def _create_event():
        from skills.calendar_skill import create_event
        return create_event(
            tool_args.get("title",""),
            tool_args.get("date_str","today"),
            tool_args.get("time_str"),
            tool_args.get("duration_mins", 60),
            tool_args.get("description",""))

    def _delete_event():
        from skills.calendar_skill import delete_event
        return delete_event(tool_args.get("title",""))

    def _next_event():
        from skills.calendar_skill import get_next_event
        return get_next_event()

    actions = {
        "open_application":    lambda: open_app(tool_args.get("app_name","")),
        "open_chrome_profile": lambda: open_chrome_profile(tool_args.get("profile_name","personal")),
        "open_website":        lambda: open_website(tool_args.get("url","")),
        "search_web":          lambda: search_web(tool_args.get("query","")),
        "get_weather":         lambda: get_weather(tool_args.get("city")),
        "tell_time":           lambda: f"It's {datetime.now().strftime('%I:%M %p')} on {datetime.now().strftime('%A, %B %d %Y')}.",
        "set_alarm":           lambda: set_alarm(tool_args.get("time_str","")),
        "set_timer":           lambda: set_timer(tool_args.get("minutes", 5)),
        "get_battery":         lambda: get_battery(),
        "get_system_info":     lambda: get_system_info(),
        "take_screenshot":     lambda: take_screenshot(),
        "get_clipboard":       lambda: get_clipboard(),
        "type_text":           lambda: type_text(tool_args.get("text","")),
        "press_key":           lambda: press_key(tool_args.get("key","")),
        "create_file":         lambda: create_file(tool_args.get("filename","notes.txt"), tool_args.get("content","")),
        "kill_process":        lambda: kill_process(tool_args.get("process_name","")),
        "remember_fact":       lambda: save_user_fact(tool_args.get("key",""), tool_args.get("value","")),
        "shutdown_pc":         lambda: shutdown_pc(),
        "restart_pc":          lambda: restart_pc(),
        "read_emails":         _read_emails,
        "send_email":          _send_email,
        "read_email_body":     _read_email_body,
        "read_screen":         _read_screen,
        "click_on_text":       _click_text,
        "double_click_text":   _double_click,
        "right_click_text":    _right_click,
        "get_active_window":   _get_active,
        "get_all_windows":     _get_all_windows,
        "focus_window":        _focus_win,
        "scroll_screen":       _scroll,
        "play_music":          _play_music,
        "control_music":       _control_music,
        "list_files":          _list_files,
        "open_file":           _open_file,
        "search_files":        _search_files,
        "read_pdf":            _read_pdf,
        "read_text_file":      _read_text,
        "delete_file":         _delete_file,
        "move_file":           _move_file,
        "create_folder":       _create_folder,
        "get_recent_files":    _recent_files,
        "open_folder":         _open_folder,
        "get_disk_usage":      _disk_usage,
        "send_whatsapp":       _send_whatsapp,
        "open_whatsapp_chat":  _open_whatsapp,
        "read_whatsapp":       _read_whatsapp,
        "manage_startup":      _manage_startup,
        "daily_summary":       _daily_summary,
        "get_todays_events":   _todays_events,
        "get_upcoming_events": _upcoming_events,
        "create_event":        _create_event,
        "delete_event":        _delete_event,
        "get_next_event":      _next_event,
    }

    fn = actions.get(tool_name)
    return fn() if fn else f"Unknown tool: {tool_name}"


def ask_brain(user_input):
    track_command(user_input)
    save_message("user", user_input)

    history  = get_recent_history(20)
    facts    = get_memory_summary()
    system   = SYSTEM_PROMPT + (f"\n\n{facts}" if facts else "")
    messages = [{"role": "system", "content": system}] + history

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=500,
            temperature=0.75
        )
    except Exception as e:
        err = str(e)
        if "rate_limit_exceeded" in err:
            import re as re2
            match = re2.search(r'try again in (\d+)m', err)
            wait  = f"{match.group(1)} minutes" if match else "a few minutes"
            raise Exception(f"Rate limit reached. Please wait {wait} and try again.")
        if "tool_use_failed" in err or "tool call validation" in err:
            try:
                fallback = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7
                )
                reply = clean_response(fallback.choices[0].message.content)
                save_message("assistant", reply)
                return reply
            except:
                raise Exception("I had trouble with that, sir. Try rephrasing.")
        raise Exception(f"Groq API error: {e}")

    message = response.choices[0].message

    if message.tool_calls:
        save_message("assistant", message.content or "")
        tool_results = []
        for tc in message.tool_calls:
            tool_name = tc.function.name
            raw_args  = tc.function.arguments
            tool_args = json.loads(raw_args) if raw_args and raw_args.strip() not in ("","null","{}") else {}
            print(f"⚡ Tool: {tool_name} | Args: {tool_args}")
            try:
                result = execute_tool(tool_name, tool_args)
            except Exception as e:
                result = f"Tool failed: {e}"
            print(f"   Result: {result}")
            tool_results.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

        tool_call_msg = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in message.tool_calls]
        }
        messages2 = [{"role": "system", "content": system}] + history + [tool_call_msg] + tool_results

        try:
            final = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages2,
                max_tokens=300,
                temperature=0.75
            )
            reply = clean_response(final.choices[0].message.content)
        except:
            reply = "Done, sir."
    else:
        reply = clean_response(message.content)

    save_message("assistant", reply)
    return reply