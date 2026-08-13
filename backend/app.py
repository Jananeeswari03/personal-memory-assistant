from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
DB = os.path.join(BASE_DIR, "memories.db")
IMAGES_DIR = os.path.join(BASE_DIR, "memory_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(fname):
    return "." in fname and fname.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT,
            category TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            remind_time TEXT,
            notified INTEGER DEFAULT 0,
            snoozed_until TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ✅ Extract key & value (clean saving)
def extract_key_and_value(text):
    t = text.replace("?", "").strip()
    lower = t.lower()

    if lower.startswith("remember that"):
        body = t[len("remember that"):].strip()
    elif lower.startswith("remember"):
        body = t[len("remember"):].strip()
    else:
        body = t

    if " is " in body:
        parts = body.split(" is ", 1)
        key = parts[0].replace("my ", "").strip()
        value = parts[1].strip()
        return key, value

    return None, body


def add_memory(key, value, category="general"):
    ts = datetime.datetime.now().isoformat()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO memories (key,value,category,timestamp) VALUES (?,?,?,?)",
        (key, value, category, ts),
    )
    conn.commit()
    conn.close()


# ✅ MAIN CHAT ROUTE
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please type something."})

    lower = message.lower()

    # ✅ Greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good night"]
    if any(lower.startswith(g) for g in greetings):
        return jsonify({"reply": "Hello! How can I assist you today?"})

    # ✅ Save memory using "remember"
    if "remember" in lower:
        key, value = extract_key_and_value(message)
        if key:
            add_memory(key, value)
            return jsonify({"reply": f"Okay, I will remember that your {key} is {value}."})
        add_memory("[note]", message, "note")
        return jsonify({"reply": "Saved as a note."})

    # ✅ Memory search
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute("SELECT key,value FROM memories ORDER BY id DESC").fetchall()
    conn.close()

    for k, v in rows:
        if not k:
            continue

        # direct question match
        if lower == k.lower():
            return jsonify({"reply": f"Your {k} is {v}."})

        # question type
        if any(q in lower for q in ["what", "which", "who", "when", "tell"]):
            if k.lower() in lower:
                return jsonify({"reply": f"Your {k} is {v}."})

        # keyword match
        if k.lower() in lower:
            return jsonify({"reply": f"{k}: {v}"})

    return jsonify({"reply": "I don't know that yet — you can save it using Save Memory or Remember."})


# ✅ Save memory manually
@app.route("/save_memory", methods=["POST"])
def save_memory():
    data = request.json or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"status": "error", "message": "Text required"}), 400

    key, value = extract_key_and_value(text)
    if not key:
        key, value = "[note]", text

    add_memory(key, value)
    return jsonify({"status": "ok", "saved": {"key": key, "value": value}})


# ✅ Image memory upload
@app.route("/upload_memory_image", methods=["POST"])
def upload_memory_image():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "file missing"}), 400

    f = request.files["file"]
    label = request.form.get("label", "")

    if f.filename == "":
        return jsonify({"status": "error", "message": "empty filename"}), 400

    if not allowed_file(f.filename):
        return jsonify({"status": "error", "message": "invalid file type"}), 400

    fname = secure_filename(f.filename)

    base, ext = os.path.splitext(fname)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    stored = f"{base}_{ts}{ext}"

    path = os.path.join(IMAGES_DIR, stored)
    f.save(path)

    key = label if label else "[image]"
    add_memory(key, stored, "image")

    return jsonify({"status": "ok", "file": stored})


@app.route("/memory_images/<path:fname>", methods=["GET"])
def memory_image(fname):
    return send_from_directory(IMAGES_DIR, fname)


# ✅ Get all memories
@app.route("/get_memories", methods=["GET"])
def get_memories():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute(
        "SELECT id,key,value,category,timestamp FROM memories ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "key": r[1], "value": r[2], "category": r[3], "timestamp": r[4]}
        for r in rows
    ])


# ✅ Reminder API
@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    data = request.json or {}
    text = data.get("text")
    remind_time = data.get("remind_time")

    if not text or not remind_time:
        return jsonify({"status": "error", "message": "text and remind_time required"}), 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO reminders (text, remind_time, notified) VALUES (?,?,0)",
        (text, remind_time),
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


@app.route("/get_reminders", methods=["GET"])
def get_reminders():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute(
        "SELECT id,text,remind_time,notified,snoozed_until FROM reminders ORDER BY remind_time"
    ).fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "text": r[1], "remind_time": r[2], "notified": r[3], "snoozed_until": r[4]}
        for r in rows
    ])


@app.route("/delete_reminder/<int:rid>", methods=["DELETE"])
def delete_reminder(rid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/snooze_reminder/<int:rid>", methods=["POST"])
def snooze_reminder(rid):
    data = request.json or {}
    minutes = int(data.get("minutes", 5))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    row = c.execute("SELECT remind_time FROM reminders WHERE id=?", (rid,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "not found"}), 404

    old_time = row[0]

    try:
        dt = datetime.datetime.fromisoformat(old_time)
    except:
        dt = datetime.datetime.now()

    new_time = dt + datetime.timedelta(minutes=minutes)

    c.execute(
        "UPDATE reminders SET remind_time=?, notified=0, snoozed_until=? WHERE id=?",
        (new_time.isoformat(), new_time.isoformat(), rid),
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "snoozed", "new_time": new_time.isoformat()})


if __name__ == "__main__":
    init_db()
    app.run(port=5000)
