import requests
import time
import sys

BASE_URL = "http://localhost:8000"
# Short video for testing (Me at the zoo, 19s)
VIDEO_URL = "https://www.youtube.com/shorts/hbrCqsJUX-M"

def test_transcription():
    print(f"Sending request for {VIDEO_URL}...")
    # API Key Configuration
    # MAKE SURE THIS MATCHES YOUR .env FILE
    API_KEY = "my_secret_key" 
    headers = {"x-api-key": API_KEY}

    try:
        # 1. Start Job
        response = requests.post(f"{BASE_URL}/api/process", json={"url": VIDEO_URL}, headers=headers)
        if response.status_code != 200:
            print(f"Error starting job: {response.text}")
            return
        
        job_id = response.json()["job_id"]
        print(f"Job started. ID: {job_id}")
        
        # 2. Poll Status
        while True:
            status_res = requests.get(f"{BASE_URL}/api/status/{job_id}", headers=headers)
            status_data = status_res.json()
            status = status_data["status"]
            
            print(f"Status: {status}")
            
            if status == "done":
                break
            if status == "error":
                print(f"Job failed: {status_data.get('error')}")
                return
            
            time.sleep(2)
            
        # 3. Get Result
        result_res = requests.get(f"{BASE_URL}/api/result/{job_id}", headers=headers)
        transcript = result_res.json()["transcript"]
        
        print("\n--- Transcription Result ---")
        print(transcript)
        print("----------------------------")

        # 4. Test Chat (Local Ollama)
        print("\nTesting Chat (Ollama)...")
        chat_question = "What is this video about? Summarize it in one sentence."
        chat_res = requests.post(f"{BASE_URL}/api/chat", json={"job_id": job_id, "question": chat_question}, headers=headers)
        
        if chat_res.status_code == 200:
            print("Chat Answer:", chat_res.json()["answer"])
        else:
            print(f"Chat failed: {chat_res.text}")
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_transcription()
