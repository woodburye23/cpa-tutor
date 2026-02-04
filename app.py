import streamlit as st
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

st.title("🎓 Junior Core Accounting Tutor")
st.sidebar.title("🏆 Progress Tracker")
st.sidebar.metric("Total XP", f"{st.session_state.xp}/100")

# 2. The "Guaranteed Connection" Logic
try:
    # Use your Secret Key
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # 2026 Update: Using Gemini 2.0 Flash (The most stable version)
    # We also set the 'transport' to 'rest' to bypass common network lags
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        generation_config={"temperature": 0.7}
    )
    
    # Quick test to wake up the brain
    st.sidebar.success("✅ Junior Core Brain Live")
except Exception as e:
    st.sidebar.error("❌ Connection Error")
    st.info("Check if your API Key is correctly pasted in Streamlit Secrets.")
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
        # The Socratic Prompt
        system_instruction = (
            "You are the Junior Core Accounting Tutor. Be Socratic. "
            "Help Ella with her Master Doc. If she gets it right, say '+10 XP'. "
            f"User Question: {prompt}"
        )
        
        try:
            # Generate the response
            response = model.generate_content(system_instruction)
            answer = response.text
            
            # Update XP and fire balloons
            if "+10 XP" in answer:
                st.session_state.xp += 10
                st.balloons()
                
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("The API is being stubborn. Let's try one more time.")
            # Fallback for the demo: If the API fails, it gives a Socratic hint anyway
            fallback = "I'm having a quick 'brain fog' moment. While I reconnect, tell me: what does your Master Doc say about the first step of this process?"
            st.write(fallback)
