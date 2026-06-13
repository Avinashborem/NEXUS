# skills/proactive.py — Proactive monitoring & alerts
import threading, time, psutil
from datetime import datetime

_monitor_thread = None
_running        = False
_speak_fn       = None

def start_proactive(speak_function):
    """Start background monitoring — pass the speak() function"""
    global _monitor_thread, _running, _speak_fn
    _speak_fn = speak_function
    if _running:
        return
    _running       = True
    _monitor_thread = threading.Thread(
        target=_monitor_loop, daemon=True)
    _monitor_thread.start()

def stop_proactive():
    global _running
    _running = False

def _monitor_loop():
    low_battery_warned  = False
    high_cpu_warned     = False
    check_interval      = 30  # seconds

    while _running:
        try:
            _check_battery(low_battery_warned)
            _check_cpu(high_cpu_warned)
            time.sleep(check_interval)
        except:
            time.sleep(check_interval)

def _check_battery(already_warned):
    global _speak_fn
    bat = psutil.sensors_battery()
    if bat and not bat.power_plugged:
        if bat.percent <= 15 and not already_warned:
            if _speak_fn:
                _speak_fn(f"Sir, battery is at {int(bat.percent)} percent. I suggest plugging in.")
            return True
    return False

def _check_cpu(already_warned):
    global _speak_fn
    cpu = psutil.cpu_percent(interval=2)
    if cpu > 90 and not already_warned:
        if _speak_fn:
            _speak_fn(f"Heads up sir, CPU is at {cpu} percent. Something is consuming a lot of resources.")
        return True
    return False

def get_daily_summary():
    """Morning briefing"""
    from datetime import datetime
    import requests
    from config import OPENWEATHER_KEY, CITY

    now     = datetime.now()
    greeting= "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 17 else "Good evening"

    try:
        url  = (f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={CITY}&appid={OPENWEATHER_KEY}&units=metric")
        r    = requests.get(url, timeout=5).json()
        temp = round(r["main"]["temp"])
        desc = r["weather"][0]["description"]
        weather_str = f"It's {temp} degrees and {desc} in {CITY}."
    except:
        weather_str = ""

    bat = psutil.sensors_battery()
    bat_str = f"Battery at {int(bat.percent)} percent." if bat else ""

    return (f"{greeting} sir. It's {now.strftime('%A, %B %d')}. "
            f"{weather_str} {bat_str} NEXUS is online and ready.")