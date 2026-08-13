# Personal Memory Assistant — Full Version (NLP + Speech + Streamlit + Transformers)

## Overview
This project is a personal memory assistant that:
- Understands and stores user "memories" (facts) in a SQLite database.
- Uses **spaCy** for NLP processing.
- Uses **Transformers** (BlenderBot / DialoGPT) for powerful conversational replies.
- Supports **voice input** (SpeechRecognition + PyAudio) and **text-to-speech** (pyttsx3).
- Provides both a minimal static HTML frontend and a Streamlit GUI.
## Features

- Store and retrieve personal memories.
- Natural language understanding using spaCy.
- Conversational AI using BlenderBot/DialoGPT.
- Voice input using SpeechRecognition.
- Text-to-speech responses using pyttsx3.
- Streamlit-based interactive interface.
- SQLite database for persistent memory storage.

## Quick start (recommended)
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. (Optional) If you plan to use the Transformers conversational model, the first run will download model weights automatically (may be large).
5. Run the Flask backend:
   ```bash
   cd backend
   python app.py
   ```
   Backend runs on http://127.0.0.1:5000 by default.
6. Run Streamlit UI (in project root):
   ```bash
   streamlit run streamlit_app.py
   ```
   Visit the URL Streamlit prints (usually http://localhost:8501).

## Notes on speech
- **PyAudio** may need system-level dependencies (e.g., PortAudio). On Ubuntu:
  ```bash
  sudo apt-get install portaudio19-dev
  pip install pyaudio
  ```
  On Windows, install the appropriate PyAudio wheel if pip install fails.
- If you cannot install PyAudio, you can still use typing-only mode.

## Files
- `backend/app.py` — Flask API and NLP/speech integrations.
- `backend/requirements.txt` — Python packages to install.
- `streamlit_app.py` — Streamlit GUI with voice controls.
- `frontend/` — simple HTML/CSS/JS chat UI (optional).

## Recommended apps
- VS Code (you already have it)
- Python 3.8+
- (Optional) Git, a browser for Streamlit UI

## Troubleshooting
- Transformer model loading can be slow and requires disk space.
- If SpeechRecognition raises `NoDefaultInputDeviceError`, check microphone availability.

## Future Enhancements

- User authentication
- Cloud synchronization
- Calendar integration
- Smart reminder scheduling
- Mobile application support


