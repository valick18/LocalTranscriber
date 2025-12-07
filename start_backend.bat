@echo off
echo Starting Local Whisper Server...

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing/Updating dependencies...
.venv\Scripts\pip install -r requirements.txt

echo Starting server...
.venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
