import streamlit as st
import google.generativeai as genai

# 1. Page Config & State
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

st.title("🎓 Junior Core Accounting Tutor")
st.sidebar.title("🏆 Progress Tracker")
st.sidebar.metric("Total XP", f"{st.session_state.xp}/100")

# 2. 2026 Connection Fix
@st.cache_resource
def init_ai():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # In 2026, 'gemini-3-flash-preview' is the high-stability model for developers
        model = genai.GenerativeModel('gemini-3-flash-preview')
        # Silent test to ensure connection
        model.generate_content("ping")
        return model
    except:
        return None

model = init_ai()

if model:
    st.sidebar.success("✅ Brain Active")
else:
    st.sidebar.error("❌ Connection Lag")
    st.info("Tip: If this stays red, try clicking 'Reboot App' in the Streamlit menu.")

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
            # Socratic system instruction included in the live call
            context = "You are a Socratic Accounting Tutor. Do not give answers. If user is correct, say +10 XP. Question: "
            response = model.generate_content(context + prompt)
            
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
                
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("The API is still foggy. Let's try the 'Presentation Backup' mode.")
            st.write("Socratic Hint: How does your Master Doc define the relationship between cost and volume?")
            
