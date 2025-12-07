# LocalTranscriber (100% Local Backend)

A powerful, **fully private** local video transcription and chat server.
It uses **Whisper** (via pywhispercpp) for transcription and **Ollama** (Llama 3, Mistral, etc.) for AI chat.
No cloud APIs. No data leaves your machine.

## Features

-   **100% Local**: No External APIs. Complete Privacy.
-   **Local Transcription**: High-performance transcription using `whisper.cpp`.
-   **Local Chat**: Ask questions about the video using your local Ollama LLM.
-   **Multilingual**: Supports 50+ languages (default: Russian).
-   **Secure**: Protected by API Key authentication (`x-api-key`).
-   **Configurable**: Run on low-end (`base` model) or high-end (`large-v3`) hardware.

## Prerequisites

1.  **Python 3.10+**
2.  **FFmpeg**: Must be installed and added to PATH.
3.  **Ollama**: Download from [ollama.com](https://ollama.com).
    -   Run `ollama pull llama3` (or your preferred model) before starting.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/valick18/LocalTranscriber.git
    cd LocalTranscriber
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
    -   `API_SECRET_KEY`: **REQUIRED**. Create a password to protect your server.
    -   `WHISPER_MODEL_NAME`: `large-v3` (Best quality, high RAM) or `base` (Fast, low RAM).
    -   `OLLAMA_MODEL`: `llama3` (or `mistral`, `gemma`, etc.).

## Usage

1.  Start the server:
    ```bash
    # Windows
    start_backend.bat
    ```

2.  The server runs at `http://localhost:8000`.

## API Documentation

**Auth**: Header `x-api-key: YOUR_SECRET_KEY` is required for all requests.

### `POST /api/process`
Start transcribing a YouTube URL.
-   **Body**: `{"url": "...", "language": "ru"}`
-   **Returns**: `{"job_id": "..."}`

### `GET /api/status/{job_id}`
Check job status.

### `GET /api/result/{job_id}`
Get the final transcript.

### `POST /api/chat`
Ask a question about the video (Requires running Ollama).
-   **Body**: `{"job_id": "...", "question": "..."}`

## Deployment (Docker)

You can deploy this as a Docker container.
1.  Make sure your host machine allows nested virtualization or CPU inference if no GPU.
2.  `docker build -t local-transcriber .`
3.  `docker run -p 8000:8000 --env-file .env local-transcriber`
