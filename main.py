import streamlit as st
import os
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load Environment & ChromaDB
load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
db_path = os.path.join("data", "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="tokyo_cleaner_knowledge")

# 2. UI Setup
st.set_page_config(page_title="Tokyo Cleaner Concierge", page_icon="🧹")
st.title("Tokyo Cleaner AI Concierge 🧹")

# 3. System Logic (The "Supreme Court")
routing_logic = """
You are the official customer service chatbot for Tokyo Cleaner.
You MUST evaluate service requests using these rules:
1. BIOHAZARD: Decline any request involving pets, accidents, feces, urine, or vomit.
2. WARD CHECK: If outside the 5 Central Wards, but within 50 mins travel and 15 mins walk, flag for manual verification at info@tokyocleaner.jp.
3. BOOKING LINKS: If the user wants to book, provide these links ONLY:
   - Express Cleaning: https://calendly.com/tokyo-cleaner/express-cleaning
   - Move Out Basic Cleaning: https://calendly.com/tokyo-cleaner/move-out-basic-cleaning
   - Residential Cleaning: https://calendly.com/tokyo-cleaner/residential-cleaning
   - Vacation Rental (Studio): https://calendly.com/tokyo-cleaner/vacation-rental-cleaning
   - Office Cleaning: https://calendly.com/tokyo-cleaner/office-cleaning
4. CONTACT ROUTING: If the request is for 1LDK+ Vacation Rental, recurring plans, or custom needs, route to: https://www.tokyocleaner.jp/contact
5. NO HALLUCINATIONS: Do not invent prices or schedules. If you don't have the info, provide the contact email/hotline: 080-8121-8105.
"""

# 4. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Process Input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Database Retrieval
    results = collection.query(query_texts=[prompt], n_results=3)
    retrieved_context = "\n".join(results["documents"][0])
    augmented_prompt = f"Knowledge Base Context:\n{retrieved_context}\n\nUser Question:\n{prompt}"

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        response = client.models.generate_content_stream(
            model='gemini-2.5-pro',
            contents=augmented_prompt,
            config=types.GenerateContentConfig(
                system_instruction=routing_logic,
                temperature=0.0
            )
        )
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})