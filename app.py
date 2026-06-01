import streamlit as st
import os
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load Environment Variables & API Key
load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# 2. Connect to the ChromaDB "Brain"
print("Connecting to local ChromaDB...")
db_path = os.path.join("data", "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="tokyo_cleaner_knowledge")

# 3. Configure Streamlit Web Interface
st.set_page_config(page_title="Tokyo Cleaner Concierge", page_icon="🧹")
st.title("Tokyo Cleaner AI Concierge 🧹")

# Sidebar Configuration
with st.sidebar:
    st.header("Admin Controls")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. The "Supreme Court" System Logic

routing_logic = """
You are the official customer service chatbot for Tokyo Cleaner.
Respond professionally in the same language as the user.
You MUST evaluate service requests using this EXACT order of operations:

STEP 1: SAFETY & BIOHAZARDS (CRITICAL OVERRIDE)
If the user mentions pets, accidents, feces, urine, or vomit, you MUST immediately decline to clean it, citing our strict biohazard safety regulations. Do NOT offer to clean the floor around it.

STEP 2: THE WARD & DISTANCE CHECK
Our primary area is the 5 Central Wards.
- If they are outside the 5 Wards, BUT the travel time is 50 MINUTES OR LESS AND they are a 15-minute walk from a station, you must state that we CAN accept the booking, but it requires manual logistics verification.
- Instruct them to email info@tokyocleaner.jp to finalize the exception.

STEP 3: SERVICE, SUPPLIES & UPSELL KNOWLEDGE (CRITICAL DATA ACCESS)
Rely STRICTLY on the knowledge base. 
- If a customer asks about specific cleaning supplies, tools, or chemicals, you MUST answer using the information provided in the "Standard Cleaning Supplies Inventory" section of the context.
- If a customer asks for deep cleaning, balcony cleaning, or trash disposal, quote the exact rules and prices from the documents. Do not invent prices or bend rules.

STEP 4: BOOKING & SCHEDULING (CRITICAL OVERRIDE)
You are a preliminary concierge. You do NOT have access to the company calendar and you CANNOT schedule dates or times in this chat. 
If a customer attempts to finalize a booking, says "book it", or provides a specific date/time, you MUST politely decline to schedule it here. 

Instead, you MUST route them to the correct link based on the specific service they want:

CALENDLY DIRECT BOOKING LINKS (For "Book Now" Services):
- Express Cleaning: "https://calendly.com/tokyo-cleaner/express-cleaning"
- Move Out Basic Cleaning: "https://calendly.com/tokyo-cleaner/move-out-basic-cleaning"
- Residential Cleaning (Monthly / 3 Hours): "https://calendly.com/tokyo-cleaner/residential-cleaning"
- Vacation Rental / Airbnb (Studio Unit ONLY): "https://calendly.com/tokyo-cleaner/vacation-rental-cleaning"
- Office Cleaning (Once a Month): "https://calendly.com/tokyo-cleaner/office-cleaning"

CONTACT FORM ROUTING (For "Contact Us" Services):
If the customer requests ANY of the following services, they cannot book directly. You MUST direct them to use this exact link -> "https://www.tokyocleaner.jp/contact"
- Any Vacation Rental / Airbnb larger than a Studio (1LDK, 2LDK, 3LDK).
- Any Weekly, Bi-Weekly, Bi-Monthly, or Mon-Fri recurring plans (for both Residential and Office).
- Any one-time standard cleaning request that doesn't fit the specific Calendly links above.

CRITICAL ROUTING RULES: 
1. NEVER ask confirmation questions like "Would you like to proceed?". Once the customer has provided enough information to determine the correct service, IMMEDIATELY provide the corresponding link. Do not stall.
2. If the user has not specified the exact plan, frequency, or room size yet, ask them to clarify before providing any link.
"""

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. User Input & Processing
if prompt := st.chat_input("How can I help you today?"):
    
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Search Vector Database for relevant rules
    results = collection.query(query_texts=[prompt], n_results=3)
    
    # Combine the found rules into a readable text block
    retrieved_context = "\n".join(results["documents"][0])
    
    # Build the final prompt for Gemini (Context + User Question)
    augmented_prompt = f"Knowledge Base Context:\n{retrieved_context}\n\nUser Question:\n{prompt}"

    # Generate and Display AI Response with Typing Effect
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        response = client.models.generate_content_stream(
            model='gemini-2.5-pro',
            contents=augmented_prompt,
            config=types.GenerateContentConfig(
                system_instruction=routing_logic,
                temperature=0.0 # Keep temperature at 0.0 so the bot doesn't hallucinate rules
            )
        )

        # Stream the text chunks live
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")
        
        # Remove cursor when finished typing
        response_placeholder.markdown(full_response)
    
    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})