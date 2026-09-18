import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": os.getenv("OPENROUTER_MODEL"),
        "messages": [
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ],
    },
    timeout=60,
)

print(response.status_code)
print(response.text)