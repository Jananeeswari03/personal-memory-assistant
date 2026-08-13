import sqlite3
import time
import datetime
import os
import winsound
import pyttsx3
import gc   # ✅ clears memory to prevent voice freeze

# ✅ Use backend database
BASE_DIR = os.path.dirname(__file__)
DB = os.path.join(BASE_DIR, "backend", "memories.db")

def speak(text):
    """Recreate TTS engine EVERY reminder = no voice stopping"""
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)

    engine.say(text)
    engine.runAndWait()
    engine.stop()
    del engine
    gc.collect()  # ✅ frees audio driver properly

def play_alarm():
    """Cute simple alarm"""
    winsound.Beep(1000, 400)
    winsound.Beep(1200, 400)

def check_reminders():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    now = datetime.datetime.now().isoformat(timespec="seconds")

    rows = c.execute("""
        SELECT id, text, remind_time 
        FROM reminders 
        WHERE notified = 0
    """).fetchall()

    for rid, text, remind_time in rows:
        if remind_time <= now:
            print(f"⏰ Reminder: {text}")

            play_alarm()
            time.sleep(0.3)  # ✅ prevents overlap
            speak(f"Reminder alert. {text}")

            c.execute("UPDATE reminders SET notified = 1 WHERE id=?", (rid,))
            conn.commit()

    conn.close()

print("🔔 Voice Reminder Engine Running…")
print(f"DB: {DB}")
print("Checking every 1 second...\n")

while True:
    try:
        check_reminders()
        time.sleep(1)  # ✅ faster & accurate timing
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
        break
    except Exception as e:
        print("Engine Error:", e)
