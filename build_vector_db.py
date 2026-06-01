import os
import chromadb

def setup_chroma_database():
    print("🔧 Initializing Local ChromaDB...")
    
    db_path = os.path.join("data", "chroma_db")
    client = chromadb.PersistentClient(path=db_path)

    try:
        client.delete_collection(name="tokyo_cleaner_knowledge")
    except:
        pass
        
    collection = client.create_collection(name="tokyo_cleaner_knowledge")

    matrix_path = os.path.join("data", "knowledge_base", "tokyo_cleaner_matrix.txt")
    
    # SAFETY CHECK 1: Ensure the file actually exists
    if not os.path.exists(matrix_path):
        print(f"🚨 ERROR: Could not find {matrix_path}")
        return

    with open(matrix_path, "r", encoding="utf-8") as file:
        text_content = file.read()

    # SAFETY CHECK 2: Ensure the file isn't empty
    if len(text_content.strip()) == 0:
        print("🚨 ERROR: The tokyo_cleaner_matrix.txt file is completely empty!")
        print("💡 FIX: Go check that file. You might need to paste the rules in it again.")
        return

    # Use a more forgiving split (single newlines instead of double)
    paragraphs = text_content.split("\n")
    
    # Only keep chunks that actually have a meaningful amount of text (over 15 characters)
    chunks = [p.strip() for p in paragraphs if len(p.strip()) > 15]

    print(f"📦 Found {len(chunks)} searchable text chunks...")

    if len(chunks) == 0:
        print("🚨 ERROR: Could not find any valid text to process.")
        return

    # Add the chunks to ChromaDB
    ids = [f"doc_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        ids=ids
    )
    
    print(f"✅ Success! Local Vector Database built at: {db_path}")

if __name__ == "__main__":
    setup_chroma_database()