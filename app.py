import streamlit as st
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

# Initialize XP and Chat History
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

# Rename and Style
st.title("🎓 Junior Core Accounting Tutor")
st.subheader("Your Personal CPA Prep Mentor")

# 2. Setup the Live Connection
try:
    # This pulls the key you saved in Streamlit Secrets
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Configure the model with your Gem's Personality
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="""
        You are the Junior Core Accounting Tutor. 
        Your personality: Supportive, professional, and Socratic.
        Your goal: Help Ella master her 'Master Doc' for the CPA exam.
        Rules: 
        1. NEVER give the final answer immediately. 
        2. Ask guiding questions to lead her to the logic.
        3. When she gets a concept right, congratulate her and include the text '+10 XP' or '+20 XP'.
        4. If she asks about Tax Basis, Cost Accounting, or Junior Core topics, use the Socratic method.
        """
    )
    st.sidebar.success("✅ AI Brain Connected")
except Exception as e:
    st.sidebar.error("❌ Connection Error")
    st.stop()

# 3. Sidebar for Gamification
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

if prompt := st.chat_input("Ask a question from your Master Doc..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate LIVE response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # The actual AI call
            response = model.generate_content(prompt)
            full_response = response.text
            
            # Update XP logic: If the AI awarded XP in its text, update the counter
            if "+10 XP" in full_response:
                st.session_state.xp += 10
                st.balloons()
            elif "+20 XP" in full_response:
                st.session_state.xp += 20
                st.balloons()

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"The AI Brain hit a snag: {e}")
