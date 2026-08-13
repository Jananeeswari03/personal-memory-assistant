@echo off
echo ==========================================
echo   STARTING PERSONAL MEMORY ASSISTANT
echo ==========================================

REM ---- START BACKEND ----
echo Starting backend...
start cmd /k "cd /d C:\Users\meena\Documents\personal-memory-assistant-pro\personal-memory-assistant-pro\backend && ..\..\venv\Scripts\activate && python app.py"

REM ---- START REMINDER ENGINE ----
echo Starting reminder engine...
start cmd /k "cd /d C:\Users\meena\Documents\personal-memory-assistant-pro && venv\Scripts\activate && python reminder_engine.py"

REM ---- START STREAMLIT ----
echo Starting Streamlit UI...
start cmd /k "cd /d C:\Users\meena\Documents\personal-memory-assistant-pro\personal-memory-assistant-pro && ..\venv\Scripts\activate && streamlit run streamlit_app.py"

echo ==========================================
echo   ALL SYSTEMS STARTED — YOU MAY CLOSE THIS
echo ==========================================
pause
