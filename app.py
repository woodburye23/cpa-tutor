import streamlit as st
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

# Initialize XP and Chat History in Session State
if 'xp' not in st.session_state: 
    st.session_state.xp = 0
if 'messages' not in st.session_state: 
    st.session_state.messages = []

# Header Section
st.title("🎓 Junior Core Accounting Tutor")
st.markdown("---")

# 2. Setup the Live Connection with Model Fix
try:
    # Use the key from your Streamlit Secrets
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # We use 'gemini-1.5-flash-latest' to avoid the 404 error
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction="""
        You are the Junior Core Accounting Tutor. 
        Your personality: Supportive, professional, and Socratic.
        Your goal: Help Ella master her 'Master Doc' for the CPA exam.
        
        Rules: 
        1. NEVER give the final answer immediately. 
        2. Ask guiding questions to lead her to the logic.
        3. If she is stuck, provide a hint based on common Junior Core accounting principles.
        4. When she gets a concept right, congratulate her and include the text '+10 XP' or '+20 XP' in your response.
        5. Keep responses concise and focused on the CPA exam logic.
        """
    )
    st.sidebar.success("✅ AI Brain Connected")
except Exception as e:
    st.sidebar.error("❌ Connection Error")
    st.error(f"Error details: {e}")
    st.stop()

# 3. Sidebar for Gamification
with st.sidebar:
    st.title("🏆 Progress Tracker")
    st.metric("Total XP", f"{st.session_state.xp}/100")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    st.info("Rank: " + ("Accounting Intern" if st.session_state.xp < 50 else "Staff Accountant"))
    
    if st.button("Clear Chat & Reset XP"):
        st.session_state.xp = 0
        st.session_state.messages = []
        st.rerun()

# 4. Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about your Master Doc..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate LIVE Socratic response
    with st.chat_message("assistant"):
        try:
            # Generate response
            response = model.generate_content(prompt)
            full_response = response.text
            
            # Logic to trigger balloons and XP update based on AI text
            if "+10 XP" in full_response:
                st.session_state.xp += 10
                st.balloons()
            elif "+20 XP" in full_response:
                st.session_state.xp += 20
                st.balloons()

            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("The AI hit a snag. Try refreshing or checking your API key.")
            st.write(f"Tech detail: {e}")
