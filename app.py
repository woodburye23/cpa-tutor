import streamlit as st
import google.generativeai as genai
import os

# 1. UI Setup (Do this FIRST so the screen isn't blank)
st.set_page_config(page_title="CPA Socratic Lab", layout="wide")

if 'xp' not in st.session_state:
    st.session_state.xp = 0

with st.sidebar:
    st.title("🏆 CPA Progress")
    st.metric("Total XP", st.session_state.xp)
    st.progress(min(st.session_state.xp / 100, 1.0))
    st.write("Status: Active")

st.title("🎓 Socratic Accounting Tutor")

# 2. Safe API Connection
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.success("AI Brain Connected!")
    else:
        st.error("API Key missing in Streamlit Secrets!")
except Exception as e:
    st.error(f"Connection Error: {e}")

# 3. Simple Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask me about your Master Doc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Simple AI Response
    try:
        response = model.generate_content(f"You are a Socratic tutor. Use a supportive tone. User says: {prompt}")
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except:
        st.write("AI is thinking... (Check your API key settings if this hangs)")
