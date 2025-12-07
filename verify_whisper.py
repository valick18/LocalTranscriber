import os
import logging
from pywhispercpp.model import Model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_whisper():
    model_name = "large-v3"
    logger.info(f"Testing Whisper model: {model_name}")
    
    try:
        # This should trigger download if not present
        model = Model(model_name, print_realtime=False, print_progress=True)
        logger.info("Model loaded successfully.")
        
        # Create a dummy wav file if possible, or just check model load
        # For now, just loading is a good step.
        # To test transcription, we need an audio file.
        
        logger.info("Verification successful: Model can be loaded.")
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")

if __name__ == "__main__":
    test_whisper()
