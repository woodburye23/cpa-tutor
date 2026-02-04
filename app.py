import streamlit as st
import google.generativeai as genai

# 1. UI Setup
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

st.title("🎓 Junior Core Accounting Tutor")
st.sidebar.title("🏆 Progress Tracker")
st.sidebar.metric("Total XP", f"{st.session_state.xp}/100")

# 2. Direct Brain Connection
# We use 'gemini-1.5-flash' - it is the most stable name globally
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.sidebar.success("✅ Brain Active")
except Exception as e:
    st.sidebar.error("❌ Key Not Found")
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
        # The prompt that makes it act like your Gem
        full_prompt = f"You are a Socratic Accounting Tutor for Junior Core. Use a supportive tone. If the user is right, say '+10 XP'. Question: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            answer = response.text
            
            if "+10 XP" in answer:
                st.session_state.xp += 10
                st.balloons()
                
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("Connection lag. Please try that message again!")
