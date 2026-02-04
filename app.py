import streamlit as st
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

st.title("🎓 Junior Core Accounting Tutor")
st.markdown("---")

# 2. Setup the Live Connection with Auto-Retry Logic
@st.cache_resource
def load_model():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Try the three most common model name variations
    model_names = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-flash-latest"]
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=name,
                system_instruction="You are the Junior Core Accounting Tutor. Be Socratic. Award '+10 XP' for right answers."
            )
            # Test if it actually works
            model.generate_content("test")
            return model
        except:
            continue
    return None

model = load_model()

if model:
    st.sidebar.success("✅ AI Brain Connected")
else:
    st.sidebar.error("❌ Connection Error")
    st.error("Google is having trouble finding the AI model. Check your API Key in Secrets.")
    st.stop()

# 3. Sidebar
with st.sidebar:
    st.title("🏆 Progress Tracker")
    st.metric("Total XP", f"{st.session_state.xp}/100")
    st.progress(min(st.session_state.xp / 100, 1.0))
    if st.button("Reset Session"):
        st.session_state.xp = 0
        st.session_state.messages = []
        st.rerun()

# 4. Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about your Master Doc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            full_response = response.text
            
            if "+10 XP" in full_response:
                st.session_state.xp += 10
                st.balloons()
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Brain Overload: {e}")
