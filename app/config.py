import os

from dotenv import load_dotenv


load_dotenv()


CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY")
CUSTOM_BASE_URL = os.getenv("CUSTOM_BASE_URL")
CUSTOM_MODEL = os.getenv("CUSTOM_MODEL")


if not CUSTOM_API_KEY:
    raise ValueError("CUSTOM_API_KEY is not set")

if not CUSTOM_BASE_URL:
    raise ValueError("CUSTOM_BASE_URL is not set")

if not CUSTOM_MODEL:
    raise ValueError("CUSTOM_MODEL is not set")