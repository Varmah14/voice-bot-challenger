import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER_1 = os.getenv("TWILIO_PHONE_NUMBER_1")
TWILIO_PHONE_NUMBER_2 = os.getenv("TWILIO_PHONE_NUMBER_2")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
NGROK_URL = os.getenv("NGROK_URL", "")
TARGET_PHONE_NUMBER = os.getenv("TARGET_PHONE_NUMBER", "+18054398008")


def get_phone_number(env_key: str) -> str:
    num = os.getenv(env_key)
    if not num:
        raise ValueError(f"Missing env var: {env_key}. Add it to your .env file.")
    return num
