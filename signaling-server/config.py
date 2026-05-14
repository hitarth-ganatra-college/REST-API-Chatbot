import os
from dotenv import load_dotenv

load_dotenv(override=True)

def getenv_required(key: str) -> str:
    val = os.environ.get(key)
    if val is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val

class Config:
    HOST = os.environ.get("SIGNALING_HOST", "0.0.0.0")
    PORT = int(os.environ.get("SIGNALING_PORT", 8765))
    ALLOWED_ORIGINS = os.environ.get("SIGNALING_ALLOWED_ORIGINS", "*").split(",")
    DEBUG = int(os.environ.get("SIGNALING_DEBUG", "1"))

if __name__ == "__main__":
    print({k: getattr(Config, k) for k in dir(Config) if not k.startswith("__")})