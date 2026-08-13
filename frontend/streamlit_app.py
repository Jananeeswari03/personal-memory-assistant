import streamlit as st
import requests, os, datetime
try:
    import speech_recognition as sr
    SR_OK = True
except:
    SR_OK = False

API = "http://127.0.0.1:5000"

st.set_page_config(page_title="Hello Kitty Memory Assistant", layout="wide")

CSS = '''
<style>
:root{--pink:#ffd5e5;--accent:#ff7aa2;--card:#fff6fb;--muted:#6b3b4a;}
html, body, .stApp { background: linear-gradient(180deg,#fff7fb 0%, #ffeef7 50%, #ffe6f3 100%); color: #3b2230; font-family: "Segoe UI", Roboto, Arial, sans-serif;}
header, footer { display:none !important; }
.app-box { margin:16px; padding:18px; border-radius:14px; background: linear-gradient(180deg,#ffffffcc,#fff0f7); box-shadow:0 12px 30px rgba(200,120,160,0.06); border:1px solid rgba(0,0,0,0.03); }
.top { display:flex; justify-content:space-between; align-items:center; }
.title { font-size:25px; font-weight:800; color:#a61257; }
.subtitle { color:#8a3a5b; }
.panel { background:var(--card); padding:12px; border-radius:12px; margin-bottom:12px; border:1px solid rgba(0,0,0,0.03); }
.chat-user { background: linear-gradient(90deg,#fff1f8,#ffe0f0); padding:10px;border-radius:14px; margin-left:auto; max-width:75%; }
.chat-bot { background: linear-gradient(90deg,#ffffff,#fff6fb); padding:10px;border-radius:14px; margin-right:auto; max-width:75%; }
.small { font-size:13px; color:#6b3b4a; }
.pink-btn > button { background:linear-gradient(90deg,#ff7aa2,#ff93b5) !important; color:white !important; font-weight:700; border-radius:10px; padding:8px 12px; box-shadow:0 8px 18px rgba(255,122,162,0.12); border:none !important; }
.rem-card { display:flex; justify-content:space-between; align-items:center; padding:10px; border-radius:10px; background:linear-gradient(90deg,#fff9fb,#fff6f8); border:1px solid rgba(170,80,110,0.03); margin-bottom:8px; }
.mem-card { padding:8px; border-radius:10px; background:linear-gradient(180deg,#ffffff,#fff6fb); margin-bottom:8px; border:1px solid rgba(170,80,110,0.03); }
.footer { text-align:center; color:#8a3a5b; margin-top:8px; font-size:13px; }
.bg-hello { position: fixed; left:0; top:0; width:100%; height:100%; z-index:-1; opacity:0.06; object-fit:cover; }
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)

assets = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(assets, exist_ok=True)
bg_local = os.path.join(assets, "hello_bg.jpg")
if os.path.exists(bg_local):
    st.markdown(f'<img class="bg-hello" src="assets/hello_bg.jpg" />', unsafe_allow_html=True)

st.markdown('<div class="app-box">', unsafe_allow_html=True)
col1, col2 = st.columns([4,1])
with col1:
    st.markdown('<div class="top"><div><div class="title">🎀 Hello Kitty Memory Assistant</div><div class="subtitle">Cute, soft, and always remembering for you</div></div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align:right;"><img src="assets/kitty_icon.png" width="72" alt="hello" /></div>', unsafe_allow_html=True)

left, right = st.columns([2,1])

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Chat", unsafe_allow_html=True)
    if "msgs" not in st.session_state:
        st.session_state.msgs = [{"from":"bot","text":"Hello! I am Hello Kitty — say 'Remember that ...' to save memories."}]
    for m in st.session_state.msgs:
        if m["from"] == "user":
            st.markdown(f'<div class="chat-user">{m["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">{m["text"]}</div>', unsafe_allow_html=True)
    row = st.text_input("Type a message", key="hk_chat_input")
    c1, c2, c3 = st.columns([1,1,1])
    if c1.button("Send", key="send"):
        txt = (row or "").strip()
        if txt:
            st.session_state.msgs.append({"from":"user","text":txt})
            try:
                res = requests.post(f"{API}/chat", json={"message": txt}, timeout=6)
                reply = res.json().get("reply","(no reply)") if res.status_code==200 else f"Backend error {res.status_code}"
            except Exception as e:
                reply = f"Error contacting backend: {e}"
            st.session_state.msgs.append({"from":"bot","text": reply})
        st.rerun()
    if c2.button("🎤 Speak", key="speak"):
        if not SR_OK:
            st.session_state.msgs.append({"from":"bot","text":"Voice not available. Install SpeechRecognition."})
            st.rerun()
        else:
            try:
                r = sr.Recognizer()
                with sr.Microphone() as src:
                    st.info("Listening...")
                    audio = r.listen(src, timeout=5, phrase_time_limit=6)
                text = r.recognize_google(audio)
                st.session_state.msgs.append({"from":"user","text":text})
                res = requests.post(f"{API}/chat", json={"message": text}, timeout=6)
                reply = res.json().get("reply","(no reply)")
                st.session_state.msgs.append({"from":"bot","text":reply})
            except Exception as e:
                st.session_state.msgs.append({"from":"bot","text":f"Voice error: {e}"})
            st.rerun()
    if c3.button("Clear Chat"):
        st.session_state.msgs = [{"from":"bot","text":"Hello! I am Hello Kitty — say 'Remember that ...' to save memories."}]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🗓️ Add Reminder", unsafe_allow_html=True)
    rdate = st.date_input("Date", datetime.date.today())
    rtime = st.time_input("Time")
    rtext = st.text_input("Reminder text", key="rem_text")
    if st.button("Add reminder"):
        if not rtext.strip():
            st.error("Type a reminder text.")
        else:
            remind_iso = datetime.datetime.combine(rdate, rtime).isoformat()
            try:
                r = requests.post(f"{API}/add_reminder", json={"text":rtext,"remind_time":remind_iso}, timeout=6)
                if r.status_code==200 and r.json().get("status")=="success":
                    st.success("Saved reminder!")
                else:
                    st.error("Save failed: "+str(r.text))
            except Exception as e:
                st.error("Backend error: "+str(e))
            st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("### 📌 Saved Reminders", unsafe_allow_html=True)
    try:
        rems = requests.get(f"{API}/get_reminders", timeout=6).json()
    except:
        rems = []
    if rems:
        for rem in rems:
            rid = rem.get("id")
            txt = rem.get("text")
            when = rem.get("remind_time") or rem.get("snoozed_until","")
            st.markdown(f'<div class="rem-card"><div><div style="font-weight:700">{txt}</div><div class="small">{when}</div></div><div></div></div>', unsafe_allow_html=True)
            coldel, colsno = st.columns([1,1])
            if coldel.button(f"Delete {rid}", key=f"del_{rid}"):
                try:
                    requests.delete(f"{API}/delete_reminder/{rid}", timeout=4)
                    st.success("Deleted")
                except Exception as e:
                    st.error("Delete failed: "+str(e))
                st.rerun()
            if colsno.button(f"Snooze 5m {rid}", key=f"snooze_{rid}"):
                try:
                    requests.post(f"{API}/snooze_reminder/{rid}", json={"minutes":5}, timeout=4)
                    st.success("Snoozed 5 minutes")
                except Exception as e:
                    st.error("Snooze failed: "+str(e))
                st.rerun()
    else:
        st.info("No reminders yet.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 📚 Memories", unsafe_allow_html=True)
    try:
        mems = requests.get(f"{API}/get_memories", timeout=6).json()
    except:
        mems = []
    if mems:
        for m in mems:
            mid = m.get("id")
            key = m.get("key") or "[note]"
            val = m.get("value") or ""
            st.markdown(f'<div class="mem-card"><strong>{key}</strong><div class="small">{val}</div></div>', unsafe_allow_html=True)
            ecol, dcol = st.columns([1,1])
            if ecol.button(f"Edit {mid}", key=f"edit_{mid}"):
                new_k = st.text_input("New key", value=key, key=f"newk_{mid}")
                new_v = st.text_input("New value", value=val, key=f"newv_{mid}")
                if st.button("Save", key=f"save_{mid}"):
                    try:
                        requests.post(f"{API}/update_memory/{mid}", json={"key":new_k,"value":new_v}, timeout=4)
                        st.success("Saved")
                    except Exception as e:
                        st.error("Save failed: "+str(e))
                        st.rerun()
    else:
        st.info("No memories yet.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🎵 Alarm sound & background", unsafe_allow_html=True)
    sound_file = st.file_uploader("Upload WAV alarm (optional) — will be saved as alarm_sounds/hello_kitty.wav", type=["wav"])
    if sound_file:
        save_path = os.path.join(os.path.dirname(__file__), "..", "alarm_sounds", "hello_kitty.wav")
        with open(save_path, "wb") as f:
            f.write(sound_file.getbuffer())
        st.success("Uploaded alarm as hello_kitty.wav")
    if st.button("Create default HelloKitty alarm"):
        try:
            import subprocess, sys
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "create_hello_kitty_sound.py")])
            st.success("Created alarm_sounds/nice_alarm.wav")
        except Exception as e:
            st.error("Create failed: "+str(e))
    if st.button("Play test alarm"):
        try:
            import winsound
            p = os.path.join(os.path.dirname(__file__), "..", "alarm_sounds", "hello_kitty.wav")
            if not os.path.exists(p):
                p = os.path.join(os.path.dirname(__file__), "..", "alarm_sounds", "nice_alarm.wav")
            if os.path.exists(p):
                winsound.PlaySound(p, winsound.SND_FILENAME)
            else:
                st.error("No alarm file found. Create/upload one.")
        except Exception as e:
            st.error("Play failed: "+str(e))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="footer">Tip: run backend + reminder_engine in separate terminals for full notifications. You can upload a background in the sidebar. ❤️</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)