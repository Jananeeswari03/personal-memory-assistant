import streamlit as st
import requests
import datetime

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Personal Memory Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE ----------
if "overview_chat_history" not in st.session_state:
    st.session_state.overview_chat_history = []

if "chat_tab_history" not in st.session_state:
    st.session_state.chat_tab_history = []


# ---------- HELPERS ----------
def send_chat(message: str):
    """Send chat message to backend."""
    try:
        r = requests.post(f"{API_URL}/chat", json={"message": message})
        return r.json().get("reply", "No response from backend")
    except Exception as e:
        return f"Backend error: {e}"


def save_memory_text(text: str):
    """Save text to memories via backend."""
    try:
        r = requests.post(f"{API_URL}/save_memory", json={"text": text})
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------- SIDEBAR ----------
st.sidebar.title("🧠 Personal Memory Assistant")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Chat & Memories", "Reminders", "Images & Media", "About"]
)

# ---------- HEADER ----------
st.title("🧠 Personal Memory Assistant")
st.caption("Smart memory, clear reminders, and email notifications.")


# ==========================================================
# ✅ PAGE — OVERVIEW
# ==========================================================
if page == "Overview":
    st.subheader("Overview")

    chat_col, side_col = st.columns([2, 1])

    # ----- LEFT: Continuous Quick Chat -----
    with chat_col:
        st.markdown("### Quick Chat")

        user_msg = st.text_input("Ask or save something", key="overview_input")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Send (chat)", key="overview_send_btn"):
                if user_msg.strip():
                    reply = send_chat(user_msg)
                    st.session_state.overview_chat_history.append(("You", user_msg))
                    st.session_state.overview_chat_history.append(("Assistant", reply))
                    st.rerun()
                else:
                    st.warning("Type something to send.")

        with c2:
            if st.button("Save to memories", key="overview_save_btn"):
                if user_msg.strip():
                    result = save_memory_text(user_msg)
                    st.session_state.overview_chat_history.append(
                        ("System", f"Saved memory: {result}")
                    )
                    st.rerun()
                else:
                    st.warning("Type something to save.")

        with c3:
            if st.button("Clear Chat", key="overview_clear_btn"):
                st.session_state.overview_chat_history = []
                st.rerun()

        st.markdown("#### Conversation")
        if st.session_state.overview_chat_history:
            for sender, text in st.session_state.overview_chat_history:
                if sender == "You":
                    st.markdown(f"🟢 **You:** {text}")
                elif sender == "Assistant":
                    st.markdown(f"🔵 **Assistant:** {text}")
                else:
                    st.markdown(f"⚙️ **System:** {text}")
        else:
            st.info("No messages yet. Say hello!")

    # ----- RIGHT: Reminders + Recent Memories -----
    with side_col:
        st.markdown("### Next Reminders")
        try:
            r = requests.get(f"{API_URL}/get_reminders")
            rems = r.json()
        except Exception as e:
            rems = []
            st.error(f"Cannot load reminders: {e}")

        if rems:
            for rem in rems[:5]:
                st.write(
                    f"**{rem['text']}** at {rem['remind_time']} • notified={rem['notified']}"
                )
        else:
            st.write("No reminders found.")

        st.markdown("### Recent Memories")
        try:
            r = requests.get(f"{API_URL}/get_memories")
            mems = r.json()
        except Exception as e:
            mems = []
            st.error(f"Cannot load memories: {e}")

        if mems:
            for m in mems[:6]:
                if m["category"] == "image":
                    st.write(f"🖼 **{m['key']}** — image memory")
                else:
                    st.write(f"📌 **{m['key']}** — {m['value']}")
        else:
            st.write("No memories stored yet.")


# ==========================================================
# ✅ PAGE — CHAT & MEMORIES
# ==========================================================
elif page == "Chat & Memories":
    st.subheader("Chat & Memories")

    chat_col, mem_col = st.columns([2, 1])

    # ----- Chat tab with its own history -----
    with chat_col:
        st.markdown("### Chat")

        chat_input = st.text_area(
            "Type your message to the assistant",
            height=120,
            key="chat_tab_input"
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Send as chat", key="chat_tab_send"):
                if chat_input.strip():
                    reply = send_chat(chat_input)
                    st.session_state.chat_tab_history.append(("You", chat_input))
                    st.session_state.chat_tab_history.append(("Assistant", reply))
                    st.rerun()
                else:
                    st.warning("Type something to send.")

        with c2:
            if st.button("Save this message", key="chat_tab_save"):
                if chat_input.strip():
                    result = save_memory_text(chat_input)
                    st.session_state.chat_tab_history.append(
                        ("System", f"Saved memory: {result}")
                    )
                    st.rerun()
                else:
                    st.warning("Type something to save.")

        with c3:
            if st.button("Clear chat history", key="chat_tab_clear"):
                st.session_state.chat_tab_history = []
                st.rerun()

        st.markdown("#### Chat history")
        if st.session_state.chat_tab_history:
            for sender, text in st.session_state.chat_tab_history:
                if sender == "You":
                    st.markdown(f"🟢 **You:** {text}")
                elif sender == "Assistant":
                    st.markdown(f"🔵 **Assistant:** {text}")
                else:
                    st.markdown(f"⚙️ **System:** {text}")
        else:
            st.info("No messages yet.")

    # ----- Quick save + search -----
    with mem_col:
        st.markdown("### Quick Save Memory")
        quick = st.text_input("Quick note text", key="quick_mem_input")
        if st.button("Quick Save", key="quick_mem_save"):
            if quick.strip():
                result = save_memory_text(quick)
                st.write(result)
            else:
                st.warning("Type something to save.")

        st.markdown("### Search in memories")
        query = st.text_input("Search question or keyword", key="search_mem_input")
        if st.button("Search", key="search_mem_btn"):
            if query.strip():
                reply = send_chat(query)
                st.write(reply)
            else:
                st.warning("Type something to search.")

    # ----- Full memory list -----
    st.markdown("### All saved memories")
    try:
        r = requests.get(f"{API_URL}/get_memories")
        mems = r.json()
    except Exception as e:
        mems = []
        st.error(f"Cannot fetch memories: {e}")

    if mems:
        for m in mems:
            if m["category"] == "image":
                st.write(f"🖼 **{m['key']}** — file: {m['value']} • {m['timestamp']}")
            else:
                st.write(f"📌 **{m['key']}** — {m['value']} ({m['category']}) • {m['timestamp']}")
    else:
        st.write("No memories yet.")


# ==========================================================
# ✅ PAGE — REMINDERS
# ==========================================================
elif page == "Reminders":
    st.subheader("Reminders")

    left, right = st.columns([1, 2])

    with left:
        st.markdown("### Add reminder")
        d = st.date_input("Date", value=datetime.date.today())
        t = st.time_input(
            "Time",
            value=(datetime.datetime.now() + datetime.timedelta(minutes=1)).time()
        )
        rem_text = st.text_input("Reminder text", key="rem_text_input")

        if st.button("Add reminder", key="add_rem_btn"):
            if not rem_text.strip():
                st.warning("Enter reminder text.")
            else:
                dt = datetime.datetime.combine(d, t)
                rt_iso = dt.isoformat()
                payload = {"text": rem_text, "remind_time": rt_iso}
                try:
                    r = requests.post(f"{API_URL}/add_reminder", json=payload)
                    st.write(r.json())
                except Exception as e:
                    st.error(f"Error adding reminder: {e}")

    with right:
        st.markdown("### Saved reminders")
        try:
            r = requests.get(f"{API_URL}/get_reminders")
            rems = r.json()
        except Exception as e:
            rems = []
            st.error(f"Cannot fetch reminders: {e}")

        if rems:
            for rem in rems:
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.write(f"**{rem['text']}**")
                    st.caption(f"{rem['remind_time']} • notified={rem['notified']}")
                with c2:
                    if st.button(f"Delete {rem['id']}", key=f"del_{rem['id']}"):
                        try:
                            requests.delete(f"{API_URL}/delete_reminder/{rem['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete error: {e}")
                with c3:
                    if st.button(f"Snooze 5m {rem['id']}", key=f"snooze_{rem['id']}"):
                        try:
                            requests.post(
                                f"{API_URL}/snooze_reminder/{rem['id']}",
                                json={"minutes": 5}
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Snooze error: {e}")
        else:
            st.write("No reminders found.")


# ==========================================================
# ✅ PAGE — IMAGES & MEDIA
# ==========================================================
elif page == "Images & Media":
    st.subheader("Images & Media")

    up_col, view_col = st.columns([1, 2])

    with up_col:
        st.markdown("### Upload image as memory")
        label = st.text_input("Image label (optional)", key="img_label_input")
        uploaded = st.file_uploader(
            "Choose image",
            type=["png", "jpg", "jpeg", "gif", "webp"],
            key="img_uploader"
        )

        if uploaded and st.button("Upload image", key="img_upload_btn"):
            files = {"file": (uploaded.name, uploaded.getvalue())}
            data = {"label": label}
            try:
                r = requests.post(f"{API_URL}/upload_memory_image", files=files, data=data)
                st.write(r.json())
            except Exception as e:
                st.error(f"Upload error: {e}")

    with view_col:
        st.markdown("### Image memories")
        try:
            r = requests.get(f"{API_URL}/get_memories")
            mems = r.json()
        except Exception as e:
            mems = []
            st.error(f"Cannot fetch memories: {e}")

        image_mems = [m for m in mems if m["category"] == "image"]
        if image_mems:
            for m in image_mems:
                st.write(f"**{m['key']}** — {m['timestamp']}")
                img_url = f"{API_URL}/memory_images/{m['value']}"
                try:
                    st.image(img_url, width=300)
                except Exception as e:
                    st.write(f"Could not load image: {e}")
        else:
            st.write("No image memories yet.")


# ==========================================================
# ✅ PAGE — ABOUT
# ==========================================================
elif page == "About":
    st.subheader("About")
    st.write("""
**Personal Memory Assistant** is a mini project that:

- Stores personal memories (like favourite things, birthdays, notes)
- Retrieves them when you ask natural questions
- Manages reminders with alarms, voice, and optional email notifications
- Supports image-based memories (photo memories)

Backend: Flask + SQLite  
Frontend: Streamlit  
Extra: A separate Python reminder engine for alarm + voice + email.
""")
