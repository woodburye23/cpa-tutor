import streamlit as st
import google.generativeai as genai
import os

# 1. Connect to the Brain
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. YOUR GEM INSTRUCTIONS (Paste yours here!)
SYSTEM_PROMPT = """
You are Ella's Socratic Accounting Tutor. 
Rules: 
- Use the provided 'Master Doc' notes (if uploaded).
- NEVER give the direct answer. Ask guiding questions.
- If she gets it right, tell her '+10 XP'.
"""

st.set_page_config(page_title="CPA Socratic Lab", layout="wide")

# Sidebar for XP
if 'xp' not in st.session_state: st.session_state.xp = 0
with st.sidebar:
    st.title("🏆 CPA Progress")
    st.metric("Total XP", st.session_state.xp)
    st.progress(min(st.session_state.xp / 100, 1.0))

# 3. The Chat Logic
st.title("🎓 Socratic Tutor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Generate response using the "Gem" logic
    full_prompt = f"{SYSTEM_PROMPT} \n\n User says: {prompt}"
    response = model.generate_content(full_prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
    
    # Simple XP logic: if the AI awards XP in the text, update the sidebar
    if "+10 XP" in response.text:
        st.session_state.xp += 10
        st.balloons()
