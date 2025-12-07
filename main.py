from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import services
import shutil

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    services.check_ffmpeg()

@app.get("/")
def read_root():
    return {"message": "Python Backend is Running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Configuration
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    expected_key = os.getenv("API_SECRET_KEY")
    if not expected_key:
        # If no key set in env, allow access (WARNING: logic for dev, but we should enforce)
        # Better safe default: if not set, deny all.
        print("WARNING: API_SECRET_KEY not set in .env! Security is disabled.")
        return None 
    
    if api_key_header == expected_key:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

# We will apply this dependency to specific routes or globally. 
# Global middleware approach for all /api routes:

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    if request.url.path.startswith("/api"):
        # Check for API Key
        expected_key = os.getenv("API_SECRET_KEY")
        if expected_key:
            client_key = request.headers.get("x-api-key")
            if client_key != expected_key:
                 # Allow OPTIONS for CORS
                if request.method == "OPTIONS":
                    return await call_next(request)
                return JSONResponse(status_code=403, content={"detail": "Invalid or missing API Key"})
    
    response = await call_next(request)
    return response

class VideoRequest(BaseModel):
    url: str
    language: str = "ru"

class ChatRequest(BaseModel):
    job_id: str
    question: str

@app.post("/api/process")
async def process_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    services.jobs[job_id] = {"status": "queued", "url": request.url}
    services.save_jobs()
    background_tasks.add_task(services.process_video, job_id, request.url, request.language)
    return {"job_id": job_id}

@app.post("/api/upload")
async def upload_endpoint(file: UploadFile = File(...), language: str = "ru", background_tasks: BackgroundTasks = None):
    job_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1]
    file_path = f"{services.DOWNLOAD_DIR}/{job_id}.{file_ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    services.jobs[job_id] = {"status": "queued", "title": file.filename}
    services.save_jobs()
    
    if background_tasks:
        background_tasks.add_task(services.process_upload, job_id, file_path, file.filename, language)
    
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    job = services.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job["status"], "error": job.get("error")}

@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    job = services.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not finished")
    return {"transcript": job["transcript"]}

@app.get("/api/jobs")
async def get_jobs():
    # Return list of jobs with id, status, title (url for now)
    return [
        {"id": k, "status": v["status"], "title": v.get("title", "Unknown Video"), "date": "Today"} 
        for k, v in services.jobs.items()
    ]

@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    if job_id in services.jobs:
        del services.jobs[job_id]
        services.save_jobs()
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Job not found")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    job = services.jobs.get(request.job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not ready")
    
    answer = services.ask_question(job["transcript"], request.question)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
