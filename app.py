import streamlit as st
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

st.title("🎓 Junior Core Accounting Tutor")
st.sidebar.title("🏆 Progress Tracker")
st.sidebar.metric("Total XP", f"{st.session_state.xp}/100")

# 2. Connection Logic with 2026 Model Names
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Update: gemini-3-flash is the current stable high-speed model
    # We use a list to try the newest models first
    model_to_use = "gemini-3-flash" 
    
    model = genai.GenerativeModel(
        model_name=model_to_use,
        system_instruction="You are a Socratic Accounting Tutor. Use a supportive tone. Award +10 XP for correct logic."
    )
    
    st.sidebar.success(f"✅ {model_to_use.upper()} Connected")
except Exception as e:
    st.sidebar.error("❌ Connection Error")
    st.stop()

# 3. Chat Logic
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about your Master Doc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Simple call without extra wrappers to avoid version conflicts
            response = model.generate_content(prompt)
            answer = response.text
            
            if "+10 XP" in answer:
                st.session_state.xp += 10
                st.balloons()
                
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("The Brain is still foggy. Try a shorter question or refresh!")
