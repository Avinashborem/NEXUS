# main.py — NEXUS Boot (HUD on main thread, voice in background)
import threading
from output.tts import speak
from voice.listener import listen
from core.intent_router import route
from config import WAKE_WORD
from output.gui import NexusHUD

hud = None

def voice_loop():
    speak("NEXUS online. All systems ready, sir.")
    hud.root.after(0, lambda: hud.add_message("nexus", "NEXUS online. All systems ready, sir."))

    while True:
        try:
            hud.root.after(0, lambda: hud.set_state("idle"))
            command = listen()

            if not command or len(command.strip()) < 2:
                continue

            if WAKE_WORD in command:
                command = command.replace(WAKE_WORD, "").strip()

            if not command:
                speak("Yes sir?")
                hud.root.after(0, lambda: hud.add_message("nexus", "Yes sir?"))
                continue

            cmd = command
            hud.root.after(0, lambda: hud.add_message("user", cmd))

            if any(w in command for w in ["goodbye", "go offline",
                                           "shut yourself down", "exit nexus"]):
                speak("Goodbye sir. NEXUS going offline.")
                hud.root.after(0, lambda: hud.add_message("nexus", "Goodbye sir. NEXUS going offline."))
                hud.root.after(1500, hud.root.destroy)
                break

            print(f"🧠 Processing: {command}")
            hud.root.after(0, lambda: hud.set_state("thinking"))

            try:
                response = route(command)
                if response:
                    resp = response
                    hud.root.after(0, lambda: hud.set_state("speaking"))
                    hud.root.after(0, lambda: hud.add_message("nexus", resp))
                    speak(response)
            except Exception as e:
                print(f"⚠ Brain error: {e}")
                msg = str(e)
                hud.root.after(0, lambda: hud.set_state("speaking"))
                hud.root.after(0, lambda: hud.add_message("nexus", msg))
                speak(msg)

        except KeyboardInterrupt:
            speak("Shutting down. Goodbye sir.")
            hud.root.after(0, hud.root.destroy)
            break
        except Exception as e:
            print(f"⚠ Error: {e}")
            continue

def run():
    global hud

    # Build HUD on main thread
    hud = NexusHUD()

    # Voice runs in background thread
    t = threading.Thread(target=voice_loop, daemon=True)
    t.start()

    # HUD mainloop runs on main thread — this blocks until window closes
    hud.root.mainloop()

if __name__ == "__main__":
    run()