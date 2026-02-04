import streamlit as st
import google.generativeai as genai
import time
import json

# 1. Page Config
st.set_page_config(page_title="Universal Study Studio", layout="wide")

# Initialize Session States
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: st.session_state.folders = {"My Projects": []}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "My Projects"
if 'mode' not in st.session_state: st.session_state.mode = "chat"
if 'sprint_end' not in st.session_state: st.session_state.sprint_end = None

# 2. Connection Logic
@st.cache_resource
def init_ai():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-3-flash-preview')
    except: return None

model = init_ai()

# 3. Smart Timer Fragment
@st.fragment(run_every=1.0)
def pomodoro_timer():
    if st.session_state.sprint_end:
        remaining = st.session_state.sprint_end - time.time()
        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            st.metric("⏳ Focus Timer", f"{mins:02d}:{secs:02d}")
        else:
            st.session_state.sprint_end = None
            st.session_state.xp += 20
            st.balloons()
            st.success("Focus Session Complete! +20 XP")
            st.rerun()
    else:
        if st.button("🚀 Start 25m Sprint"):
            st.session_state.sprint_end = time.time() + (25 * 60)
            st.rerun()

# 4. Sidebar: Tools & Navigation
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    pomodoro_timer()

    st.divider()
    st.subheader("📂 Project Folders")
    new_folder = st.text_input("New Project Name", placeholder="e.g. History Exam")
    if st.button("Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder
            st.rerun()

    st.session_state.current_folder = st.selectbox("Current Project", list(st.session_state.folders.keys()))

    st.divider()
    # Navigation Modes
    if st.button("💬 Universal Chat"): st.session_state.mode = "chat"
    if st.button("📝 Custom Quiz Gen"): st.session_state.mode = "quiz"
    if st.button("🗂️ Flashcard Gen"): st.session_state.mode = "flashcards"
    
    st.divider()
    uploaded_file = st.file_uploader("Upload Source Material", type=['pdf', 'txt'])

# 5. Main Content Area
st.title(f"🚀 {st.session_state.current_folder}")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: CUSTOM QUIZ GENERATOR ---
if st.session_state.mode == "quiz":
    st.header("🎯 Custom Quiz Generator")
    quiz_topic = st.text_input("What should the quiz be about?", placeholder="e.g. 10 questions on Bio Chemistry or a quiz based on my upload")
    
    if st.button("Build Quiz Now"):
        with st.spinner("Writing your quiz..."):
            # Context builder
            user_context = f"Topic: {quiz_topic}. Project Folder: {st.session_state.current_folder}."
            if uploaded_file:
                user_context += " Reference the uploaded file for content."
            
            res = model.generate_content(f"You are a professional quiz maker. Create a quiz based on this request: {user_context}. Provide the questions followed by an answer key.")
            st.markdown(res.text)

# --- MODE: FLASHCARDS ---
elif st.session_state.mode == "flashcards":
    st.header("🗂️ Smart Flashcards")
    card_topic = st.text_input("What topic for the cards?", placeholder="e.g. French vocab")
    if st.button("Generate Cards"):
        with st.spinner("Generating cards..."):
            res = model.generate_content(f"Create 5 flashcards for {card_topic}. Format: Question / Answer.")
            st.markdown(res.text)

# --- MODE: CHAT (Default) ---
else:
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Chat about {st.session_state.current_folder}..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # Now a generic helpful tutor
            sys_msg = f"You are a helpful study assistant. Current Project: {st.session_state.current_folder}. User: {prompt}"
            response = model.generate_content(sys_msg)
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
