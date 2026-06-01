import os
from dotenv import load_dotenv
import chromadb
from google import genai
from google.genai import types

# Load API Key from .env
load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_chatbot_response(user_question):
    # 1. Connect to the local vector database
    db_path = os.path.join("data", "chroma_db")
    db_client = chromadb.PersistentClient(path=db_path)
    collection = db_client.get_collection(name="tokyo_cleaner_knowledge")
    
    # 2. Search: Retrieve top 6 chunks to maximize context window
    results = collection.query(
        query_texts=[user_question],
        n_results=6
    )
    
    # Flatten the results into a context string
    retrieved_context = "\n".join(results['documents'][0])
    
    # 3. System Instructions: Instructing the Pro model to be helpful but strict
    system_instruction = f"""
    You are the official Website Chatbot for Tokyo Cleaner.
    Your role is to answer customer queries professionally in the same language as the user (English or Japanese).
    
    CRITICAL RULES:
    1. Base your answer ONLY on the provided KNOWLEDGE BASE.
    2. Do not hallucinate prices or services not mentioned.
    3. If the answer is not in the knowledge base, politely apologize and refer them to info@tokyocleaner.jp.
    
    KNOWLEDGE BASE:
    {retrieved_context}
    """
    
    # 4. Generate response using the authorized Pro-tier model
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=user_question,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1
        )
    )
    
    return response.text

if __name__ == "__main__":
    print("\n=============================================")
    print(" 🤖 TOKYO CLEANER WEBSITE CHATBOT (Type 'exit' to quit)")
    print("=============================================\n")
    
    while True:
        user_input = input("Customer: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        print("\nSearching database and thinking...")
        try:
            answer = get_chatbot_response(user_input)
            print(f"\nChatbot: {answer}\n")
        except Exception as e:
            print(f"\n[Error]: Could not retrieve response. {e}\n")
        print("-" * 45)