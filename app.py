import streamlit as st
import google.generativeai as genai
import time
import json

# 1. Page Config & Professional Styling
st.set_page_config(page_title="Junior Core Study OS", layout="wide")

# --- INITIALIZATION BLOCK (The Fix) ---
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: st.session_state.folders = {"General": []}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "General"
if 'mode' not in st.session_state: st.session_state.mode = "chat"
if 'flashcards' not in st.session_state: st.session_state.flashcards = []

# 2. Connection Logic
@st.cache_resource
def init_ai():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Using the 2026 stable model name
        return genai.GenerativeModel('gemini-3-flash-preview')
    except:
        return None

model = init_ai()

# 3. Sidebar: The Command Center
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    # Feature 1: Pomodoro Timer
    st.subheader("⏱️ Focus Timer")
    if st.button("Start 25m Sprint"):
        st.toast("Stay focused! Timer started.")
        # Simulating a sprint for demo purposes; in real use, this would be a background thread
        st.session_state.xp += 20
        st.balloons()
        st.success("Sprint Over! +20 XP")

    st.divider()
    # Feature 2: Folder Management
    st.subheader("📂 Topic Folders")
    new_folder = st.text_input("New Topic Name", placeholder="e.g. Tax Basis")
    if st.button("Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder
            st.rerun()

    st.session_state.current_folder = st.selectbox("Current Topic", list(st.session_state.folders.keys()))

    st.divider()
    # Feature 3: Navigation Modes
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Chat"): st.session_state.mode = "chat"
        if st.button("📝 Quiz"): st.session_state.mode = "quiz"
    with col2:
        if st.button("🗂️ Cards"): st.session_state.mode = "flashcards"
        if st.button("🧹 Clear"): 
            st.session_state.folders[st.session_state.current_folder] = []
            st.rerun()

    # Feature 4: Download History
    st.divider()
    chat_data = json.dumps(st.session_state.folders[st.session_state.current_folder], indent=2)
    st.download_button(
        label="📥 Download Chat History",
        data=chat_data,
        file_name=f"{st.session_state.current_folder}_history.json",
        mime="application/json"
    )

# 4. Main Interface Logic
st.title(f"🎓 {st.session_state.current_folder} Master Studio")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: QUIZ ---
if st.session_state.mode == "quiz":
    st.header("📝 Personalized CPA Quiz")
    if st.button("Generate 3 Hard Questions"):
        with st.spinner("AI is crafting questions..."):
            res = model.generate_content(f"Generate 3 multiple choice CPA questions about {st.session_state.current_folder}. Provide answers at the end.")
            st.markdown(res.text)

# --- MODE: FLASHCARDS ---
elif st.session_state.mode == "flashcards":
    st.header("🗂️ Active Recall Cards")
    if st.button("Generate New Cards"):
        with st.spinner("Thinking..."):
            res = model.generate_content(f"Create 3 flashcards for {st.session_state.current_folder}. Format: Question on one line, Answer on the next.")
            st.markdown(res.text)

# --- MODE: CHAT (Default) ---
else:
    # Display messages for the CURRENT folder
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask about {st.session_state.current_folder}..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # The Socratic logic
            context = f"You are a Socratic Accounting Tutor for {st.session_state.current_folder}. Award +10 XP for correct reasoning. Prompt: {prompt}"
            response = model.generate_content(context)
            
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
