import os
from dotenv import load_dotenv
from google import genai

# Load the API key from your .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)

print("Checking connection to Gemini...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Tell me in five words or less if you can hear me.'
)

print("\n--- Gemini Response ---")
print(response.text)
print("-----------------------\n")