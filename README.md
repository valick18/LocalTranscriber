# Content Transcriber (Local Backend)

A powerful local video transcription and chat server using OpenAI's **Whisper** (via pywhispercpp) and **Groq** (for AI chat).

## Features

-   **Local Transcription**: Uses `whisper.cpp` (via `pywhispercpp`) for high-performance, private transcription.
-   **Multilingual Support**: Supports transcribing 50+ languages (default: Russian).
-   **AI Chat**: Chat with the content of your video using Llama 3 (via Groq API).
-   **Security**: Protected by API Key authentication.
-   **Configurable**: Easily switch between Whisper model sizes (base, small, large-v3) based on your hardware.

## Prerequisites

-   **Python 3.10+**
-   **FFmpeg**: Must be installed and added to PATH. (Used for audio extraction).

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/transcriber_local.git
    cd transcriber_local
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```

2.  Edit `.env` and set your variables:
    -   `GROQ_API_KEY`: Get one from [console.groq.com](https://console.groq.com).
    -   `API_SECRET_KEY`: **Important!** Set a strong password here. This protects your server.
    -   `WHISPER_MODEL_NAME`: Choose `base` (fast, low RAM) or `large-v3` (high accuracy, high RAM).

## Usage

1.  Start the server:
    ```bash
    # Windows
    start_backend.bat
    # Or manually:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

2.  The server will be available at `http://localhost:8000`.

## API Documentation

All API endpoints start with `/api/`.
You **MUST** include the header `x-api-key: YOUR_SECRET_KEY` in every request.

### `POST /api/process`
Start transcribing a YouTube URL.
-   **Body**: `{"url": "...", "language": "ru"}`
-   **Returns**: `{"job_id": "..."}`

### `GET /api/status/{job_id}`
Check job status.

### `GET /api/result/{job_id}`
Get the final transcript.

### `POST /api/chat`
Ask a question about the video.
-   **Body**: `{"job_id": "...", "question": "..."}`

## Security

This server is protected by a simple API Key mechanism.
-   The `main.py` middleware checks for the `x-api-key` header.
-   If the header is missing or does not match `API_SECRET_KEY` in `.env`, the request is rejected (403 Forbidden).
-   **Do not share your API_SECRET_KEY**.
