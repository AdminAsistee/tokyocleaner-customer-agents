import chromadb
import os
import glob

print("Connecting to ChromaDB...")
db_path = os.path.join("data", "chroma_db")
client = chromadb.PersistentClient(path=db_path)

# 1. Wipe the old memory clean so we don't get duplicates
try:
    client.delete_collection(name="tokyo_cleaner_knowledge")
    print("Old memory wiped.")
except Exception:
    pass

collection = client.create_collection(name="tokyo_cleaner_knowledge")

# 2. Find ALL text files in the knowledge_base folder
kb_dir = os.path.join("data", "knowledge_base")
txt_files = glob.glob(os.path.join(kb_dir, "*.txt"))

all_paragraphs = []

# 3. Sweep through the files and extract the rules
for file_path in txt_files:
    print(f"Reading {os.path.basename(file_path)}...")
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
        # Split into chunks based on double line breaks
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        all_paragraphs.extend(paragraphs)

# 4. Generate unique IDs and inject everything into the AI
ids = [f"rule_block_{i}" for i in range(len(all_paragraphs))]

if all_paragraphs:
    collection.add(documents=all_paragraphs, ids=ids)
    print(f"\n✅ SUCCESS! {len(all_paragraphs)} business rules permanently injected into the AI's brain.")
else:
    print("Error: No text found in the knowledge_base folder.")