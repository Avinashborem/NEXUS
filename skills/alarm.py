# skills/alarm.py — Real Alarm System
import threading
import time
from datetime import datetime, timedelta

active_alarms = []

def set_alarm(time_str):
    try:
        now = datetime.now()
        time_str = time_str.strip().upper()
        try:
            alarm_time = datetime.strptime(time_str, "%I:%M %p").replace(
                year=now.year, month=now.month, day=now.day)
        except:
            alarm_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day)

        if alarm_time < now:
            alarm_time += timedelta(days=1)

        delay = (alarm_time - now).total_seconds()

        def ring():
            time.sleep(delay)
            _trigger_alarm(time_str)

        t = threading.Thread(target=ring, daemon=True)
        t.start()
        active_alarms.append({"time": time_str, "thread": t})

        minutes = int(delay // 60)
        seconds = int(delay % 60)
        if minutes > 0:
            return f"Alarm set for {time_str}. That's {minutes} minutes from now."
        else:
            return f"Alarm set for {time_str}. That's {seconds} seconds from now."
    except Exception as e:
        return f"Couldn't set alarm: {e}. Please say the time clearly like 5:30 PM."


def _trigger_alarm(time_str):
    import winsound
    from output.tts import speak
    speak(f"Sir, your alarm for {time_str} is going off now.")
    for _ in range(5):
        winsound.Beep(1000, 500)
        time.sleep(0.3)


def set_timer(minutes):
    try:
        mins = int(minutes)
        def ring():
            time.sleep(mins * 60)
            _trigger_alarm(f"{mins} minute timer")
        t = threading.Thread(target=ring, daemon=True)
        t.start()
        return f"Timer set for {mins} minutes."
    except Exception as e:
        return f"Couldn't set timer: {e}"


def list_alarms():
    if not active_alarms:
        return "No active alarms, sir."
    return "Active alarms: " + ", ".join([a["time"] for a in active_alarms])