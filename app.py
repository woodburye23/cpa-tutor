import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader # You might need to add this to requirements.txt

# 1. Setup Brain
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Function to read your Master Docs
def get_pdf_text():
    text = ""
    # This looks for any PDF you uploaded to your GitHub folder
    for file in os.listdir():
        if file.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    return text

# 3. Load the knowledge once
if "knowledge_base" not in st.session_state:
    with st.spinner("Reading your Master Docs..."):
        st.session_state.knowledge_base = get_pdf_text()

# 4. Socratic Logic
SYSTEM_PROMPT = f"""
You are Ella's Socratic CPA Tutor. 
KNOWLEDGE BASE FROM MASTER DOCS: {st.session_state.knowledge_base[:5000]} 

RULES:
- Never give the answer.
- Reference the Master Doc concepts specifically.
- Award '+10 XP' for good logic.
"""

# ... (Rest of your chat UI code)
