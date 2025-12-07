import os
import glob
import json
import uuid
import logging
import yt_dlp
import subprocess
import ollama
from dotenv import load_dotenv
from pywhispercpp.model import Model

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
# client = Groq(api_key=GROQ_API_KEY) # REMOVED

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

JOBS_FILE = "jobs.json"

# Initialize Whisper Model (Global to avoid reloading)
# You can change 'base.en' to 'large-v3' or others. 
# It will download the model automatically on first run.
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "large-v3") 
logger.info(f"Initializing Whisper model: {WHISPER_MODEL_NAME}...")
try:
    whisper_model = Model(WHISPER_MODEL_NAME, print_realtime=False, print_progress=True)
    logger.info("Whisper model initialized.")
except Exception as e:
    logger.error(f"Failed to initialize Whisper model: {e}")
    whisper_model = None

def load_jobs():
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_jobs():
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

jobs = load_jobs()

def check_ffmpeg():
    import shutil
    if not shutil.which("ffmpeg"):
        logger.error("FFmpeg not found! Please install FFmpeg and add it to your PATH.")

def transcribe_file_local(file_path: str, language: str = "ru") -> str:
    if not whisper_model:
        raise Exception("Whisper model not initialized.")
    
    logger.info(f"Transcribing {file_path} locally...")
    segments = whisper_model.transcribe(file_path, language=language)
    # segments is a list of Segment objects or similar depending on version, 
    # pywhispercpp usually returns a list of segments where each has 'text'.
    full_text = " ".join([seg.text for seg in segments])
    return full_text

def process_video(job_id: str, url: str, language: str = "ru"):
    try:
        jobs[job_id]["status"] = "downloading"
        save_jobs()
        
        # 1. Download Audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_DIR}/{job_id}.%(ext)s',
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        audio_path = f"{DOWNLOAD_DIR}/{job_id}.mp3"
        
        # 3. Transcribe
        jobs[job_id]["status"] = "transcribing"
        save_jobs()
        
        # Use local whisper
        # Note: whisper.cpp might prefer wav 16kHz, but pywhispercpp often handles conversion or ffmpeg does.
        # Let's ensure it's compatible. pywhispercpp uses ffmpeg internally usually.
        full_transcript = transcribe_file_local(audio_path, language=language)
        
        # Cleanup
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["transcript"] = full_transcript.strip()
        jobs[job_id]["title"] = url # Placeholder title
        save_jobs()
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        save_jobs()

def process_upload(job_id: str, file_path: str, original_filename: str, language: str = "ru"):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["title"] = original_filename
        save_jobs()
        
        audio_path = file_path
            
        # 3. Transcribe
        jobs[job_id]["status"] = "transcribing"
        save_jobs()
        
        full_transcript = transcribe_file_local(audio_path, language=language)
        
        # Cleanup
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["transcript"] = full_transcript.strip()
        save_jobs()
        
    except Exception as e:
        logger.error(f"Upload job failed: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        save_jobs()

def ask_question(transcript: str, question: str):
    try:
        logger.info(f"Asking question: {question}")
        model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Truncate transcript to avoid context window limits (Ollama models vary)
        max_chars = 15000 
        if len(transcript) > max_chars:
            logger.warning("Transcript too long, truncating...")
            truncated_transcript = transcript[:max_chars] + "...[TRUNCATED]"
        else:
            truncated_transcript = transcript

        response = ollama.chat(model=model, messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the user's question based ONLY on the provided video transcript. If the answer is not in the transcript, say so."
            },
            {
                "role": "user",
                "content": f"Transcript: {truncated_transcript}\n\nQuestion: {question}"
            }
        ])
        return response['message']['content']
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return f"Error: {str(e)} - Make sure Ollama is running (ollama serve) and model is pulled (ollama pull {model})"
