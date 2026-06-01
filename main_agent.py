import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

def load_knowledge_base():
    matrix_path = os.path.join("data", "knowledge_base", "tokyo_cleaner_matrix.txt")
    with open(matrix_path, "r", encoding="utf-8") as file:
        return file.read()

# ---------------------------------------------------------
# THE TOOL: Upgraded with Error Catching
# ---------------------------------------------------------
def check_cleaner_availability(day_of_week: str) -> str:
    """Checks the company schedule database for available cleaning slots on a specific day."""
    clean_day = day_of_week.strip().lower() 
    print(f"   [⚙️ TOOL FIRED] Gemini requested: '{day_of_week}'")
    
    schedule_path = os.path.join("data", "schedule_db.json")
    
    try:
        with open(schedule_path, "r", encoding="utf-8") as file:
            schedule = json.load(file)
            
        day_data = schedule.get(clean_day, {"status": "Database Error - Day missing", "available_slots": []})
        print(f"   [🔍 TOOL RETURNING TO AI] -> {day_data}")
        return json.dumps(day_data)
        
    except Exception as e:
        # If Python crashes, print it to the terminal AND hand the error to Gemini
        error_msg = f"PYTHON CRASH: {str(e)}"
        print(f"   [🚨 {error_msg}]")
        return json.dumps({"error": error_msg})

def run_concierge_agent(sender_email, incoming_email_text):
    knowledge_base = load_knowledge_base()
    
    print("🚦 ROUTE B: Processing free-form customer inquiry with Live Calendar Access...")
    
    system_instruction = f"""
    You are the Tokyo Cleaner AI Concierge. 
    
    AGENT WORKFLOW:
    1. Read the customer email.
    2. If they ask for a specific day, you MUST use the `check_cleaner_availability` tool. 
    3. Read the exact JSON data returned by the tool.
    4. Write your email reply based explicitly on the tool's schedule data.
    
    REFERENCE MATRIX:
    {knowledge_base}
    
    FINAL OUTPUT FORMAT:
    You must output your final response as a JSON object matching this structure:
    {{
        "ticket_type": "CUSTOMER_INQUIRY",
        "agent_draft_reply": "Your drafted email to the customer. Tell them the exact open times from the tool data."
    }}
    """

    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[check_cleaner_availability], 
            temperature=0.1
        )
    )
    
    response = chat.send_message(f"Incoming Email:\n{incoming_email_text}")
    return response.text

if __name__ == "__main__":
    
    customer_sender = "arnav@example.com"
    customer_email = "Hi team, I need a standard cleaning next week. Can you guys come on Thursday? If not, what about Friday?"
    
    print("\n--- INITIATING AGENT PROTOCOL ---")
    customer_result = run_concierge_agent(customer_sender, customer_email)
    
    clean_result = customer_result.replace("```json", "").replace("```", "").strip()
    
    print("\n================ FINAL JSON OUTPUT ================")
    print(clean_result)
    print("===================================================\n")