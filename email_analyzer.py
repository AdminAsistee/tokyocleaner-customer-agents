import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Load API Key
load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# 2. Define the exact JSON structure
class ClientProfile(BaseModel):
    customer_email: str = Field(description="Extract the sender's email address")
    primary_concern: str = Field(description="Categorize as: Booking, Complaint, Inquiry, or Modification")
    customer_urgency: str = Field(description="Categorize as: Low, Medium, High, or Critical")
    communication_style: str = Field(description="Categorize as: Formal, Casual, Frantic, or Aggressive")

# 3. The Strict System Instruction
extraction_rules = """
You are a backend data pipeline for Tokyo Cleaner.
Your ONLY job is to read raw customer emails and extract the requested data.
Do not write pleasantries. Do not write email replies. 
Output ONLY valid JSON matching the exact schema provided.
"""

# 4. The Batch of Messy Emails (The Inbox)
email_inbox = [
    # Email 1: The Frantic Rush
    """
    Subject: URGENT: Cleaning before in-laws arrive!!
    From: kenji.tanaka@email.com
    I am absolutely panicking right now. My in-laws are flying in this Saturday and my 3LDK in Chiyoda is a complete disaster. I really need someone to do a deep clean before they get here!
    """,
    
    # Email 2: The Corporate Suit
    """
    Subject: Inquiry regarding corporate rates
    From: sarah.smith@corporate-holdings.jp
    Good morning Tokyo Cleaner team. I am writing to formally request a pricing matrix for routine cleanings of our corporate apartments located in Minato-ku. Please advise at your earliest convenience.
    """,
    
    # Email 3: The Casual Mod
    """
    Subject: change my time?
    From: arnav12n@gmail.com
    hey guys, can we bump my cleaning tomorrow back by like 2 hours? kinda double booked myself lol. thanks.
    """
]

# 5. Execute the Batch Processing Loop
print("Initializing Antigravity Batch Processing...\n")

# This empty list will hold all our final JSON packets
extracted_database = []

for index, email in enumerate(email_inbox):
    print(f"Processing Email {index + 1}...")
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=email,
        config=types.GenerateContentConfig(
            system_instruction=extraction_rules,
            temperature=0.0, 
            response_mime_type="application/json",
            response_schema=ClientProfile, 
        )
    )
    
    # Parse the AI's JSON string into a real Python dictionary
    clean_data = json.loads(response.text)
    
    # Append the clean data to our master list
    extracted_database.append(clean_data)

# 6. Print the final aggregated data block
print("\n--- FINAL BATCH JSON READY FOR CLOUD DATABASE ---")
print(json.dumps(extracted_database, indent=4))