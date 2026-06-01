# Tokyo Cleaner AI Concierge 🫧

## 📖 Overview
The Tokyo Cleaner AI Concierge is a high-performance, policy-compliant customer service assistant. Built for the Tokyo service market, it uses a **Retrieval-Augmented Generation (RAG)** architecture to provide accurate quotes, enforce service area logic, and route bookings to the appropriate conversion channels.

## 🚀 Core Features
* **Policy-Compliant RAG:** Uses a ChromaDB-backed knowledge base to ensure all responses strictly adhere to company pricing and service rules.
* **Geographic Intelligence:** Automatically parses customer location data to determine service eligibility within the 5 Central Wards.
* **Intelligent Routing:** Dynamically funnels users between direct Calendly booking links and custom inquiry forms based on service complexity.
* **Safety Protocols:** Hard-coded "Supreme Court" logic to identify and decline biohazard-related service requests.
* **"Soap Bubble" Memory Management:** Features a volatile, reset-capable session state that ensures data privacy and prevents context leakage between separate customer inquiries.

## 🛠️ Technical Stack
* **Framework:** [Streamlit](https://streamlit.io/)
* **Intelligence Engine:** [Google Gemini 1.5 Pro](https://ai.google.dev/)
* **Vector Database:** [ChromaDB](https://www.trychroma.com/)
* **Language:** Python 3.10+

## ⚙️ Setup & Installation
1. **Clone the repository:**
   ```bash

   //Install dependencies 
   pip install -r requirements.txt

   //Configure Environment Variables:
   GOOGLE_API_KEY=your_gemini_api_key_here

   //Run the application 
   streamlit run app.py

## 🏗️ Architecture Flow
The application operates on an **Input → Filter → Route** pipeline:



1. **Input:** User query captured via Streamlit interface.
2. **Filter:** Prompt queried against ChromaDB to retrieve relevant company policy snippets.
3. **Route:** Gemini synthesizes context with system instructions to generate a compliant response.
