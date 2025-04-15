import logging
from .config import (
    DEVICE, 
    BATCH_SIZE,
    COMPUTE_TYPE,
    MODEL
)

# 获取 logger
logger = logging.getLogger('shortcap.transcriber')

class TranscriptionError(Exception):
    """Custom exception class for handling errors during transcription"""
    pass

def transcribe_with_api(
    audio_file,
    prompt: str | None = None 
):
    exit()
    return []

def transcribe_locally(
    audio_file: str,
    align_words : bool
):
    """
    Transcribe an audio file using the local Whisper package
    (https://pypi.org/project/openai-whisper/)
    """
    try:
        import whisperx
    except ImportError:
        logger.error("Unable to import whisperx module. Make sure whisperx is installed.")
        raise TranscriptionError("Unable to import whisperx module. Make sure whisperx is installed.")

    try:
        logger.info("Loading Whisper model")
        model = whisperx.load_model(MODEL, DEVICE, compute_type=COMPUTE_TYPE)
    except Exception as e:
        logger.error(f"Error loading Whisper model: {str(e)}")
        raise TranscriptionError(f"Failed to load Whisper model: {str(e)}")

    try:
        logger.info("Starting local transcription")
        result = model.transcribe(audio_file, batch_size=BATCH_SIZE)
        logger.info("Local transcription completed successfully")
    except Exception as e:
        logger.error(f"Error during local transcription: {str(e)}")
        raise TranscriptionError(f"Local transcription failed: {str(e)}")
    
    if align_words:
        try:
            logger.info("Starting alignment")
            model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)
            result = whisperx.align(result["segments"], model_a, metadata, audio_file, DEVICE, return_char_alignments=False)
            logger.info("Alignment completed successfully")
        except Exception as e:
            logger.error(f"Error during local transcription: {str(e)}")
            raise TranscriptionError(f"Local transcription failed: {str(e)}")
        
    print(result["segments"])

    return result["segments"]