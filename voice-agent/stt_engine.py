import requests
from config import Config

OPENAI_URL = "https://api.openai.com/v1/audio/transcriptions"

def stt_whisper(audio_path):
    headers = {"Authorization": f"Bearer {Config.WHISPER_KEY}"}
    files = {
        "file": (audio_path, open(audio_path, "rb"), "audio/wav"),
        "model": (None, "whisper-1"),
    }
    response = requests.post(OPENAI_URL, headers=headers, files=files)
    response.raise_for_status()
    j = response.json()
    return j['text'], float(j.get('confidence', 1.0))  # Whisper API may not always return confidence.