import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable '{key}' is not set.")
    return value

def get_env_default(key: str, default, cast=None):
    value = os.getenv(key, default)
    if cast and value is not None:
        try:
            value = cast(value)
        except ValueError:
            raise ValueError(f"Environment variable '{key}' cannot be cast to {cast.__name__}.")
    return value

class Config:
    SESSION_ID = get_env("SESSION_ID")
    SIGNALING_SERVER_URL = get_env("SIGNALING_SERVER_URL")
    WHISPER_KEY = get_env("WHISPER_KEY")
    
    DB_URL = get_env("DB_URL")
    
    CHATBOT_API_URL = get_env("CHATBOT_API_URL")
    CHATBOT_API_KEY = get_env("CHATBOT_API_KEY")
    
    TENANT_ID = get_env("TENANT_ID")
    OUTLET_ID = get_env("OUTLET_ID")
    USER_ID = get_env("USER_ID")
    
    TTS_MODE = get_env_default("TTS_MODE", "client")
    TTS_VOICE = get_env_default("TTS_VOICE", None)

def get_config() -> Config:
    return Config

if __name__ == "__main__":
    config = get_config()
    for attr in dir(config):
        if attr.isupper():
            print(f"{attr}: {getattr(config, attr)}")
    print("Configuration loaded successfully.")