import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
# Make sure this matches the name in your .env file
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

print("🔍 Searching for available models...")
models = client.models.list()
for model in models:
    print(f"Found model: {model.name}")