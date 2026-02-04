import streamlit as st
import google.generativeai as genai
import time
import json

# 1. Page Config
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

# Initialize Session States
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: st.session_state.folders = {"Junior Core": []}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "Junior Core"
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
            st.metric("⏳ Accounting Focus Timer", f"{mins:02d}:{secs:02d}")
        else:
            st.session_state.sprint_end = None
            st.session_state.xp += 20
            st.balloons()
            st.success("Study Session Complete! +20 XP")
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
    st.subheader("📂 Topic Folders")
    new_folder = st.text_input("New Topic Name", placeholder="e.g. Cost Accounting")
    if st.button("Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder
            st.rerun()

    st.session_state.current_folder = st.selectbox("Current Topic", list(st.session_state.folders.keys()))

    st.divider()
    # Navigation Modes
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Custom Quiz Gen"): st.session_state.mode = "quiz"
    if st.button("🗂️ Flashcard Gen"): st.session_state.mode = "flashcards"
    
    st.divider()
    uploaded_file = st.file_uploader("Upload Master Doc Material", type=['pdf', 'txt'])

# 5. Main Content Area
st.title(f"🎓 {st.session_state.current_folder} Studio")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: CUSTOM ACCOUNTING QUIZ ---
if st.session_state.mode == "quiz":
    st.header("🎯 Custom Accounting Quiz")
    quiz_topic = st.text_input("What accounting topic should I test you on?", placeholder="e.g. 5 questions on Lease Accounting logic")
    
    if st.button("Generate Quiz"):
        with st.spinner("Analyzing accounting standards..."):
            user_context = f"Topic: {quiz_topic}. Topic Folder: {st.session_state.current_folder}."
            if uploaded_file:
                user_context += " Reference the uploaded master doc notes for content."
            
            res = model.generate_content(f"You are a professional Accounting Professor. Create a quiz based on this request: {user_context}. Provide the questions followed by a detailed explanation for each answer.")
            st.markdown(res.text)

# --- MODE: FLASHCARDS ---
elif st.session_state.mode == "flashcards":
    st.header("🗂️ Active Recall Cards")
    card_topic = st.text_input("Topic for flashcards?", placeholder="e.g. Consolidation entries")
    if st.button("Generate Cards"):
        with st.spinner("Generating cards..."):
            res = model.generate_content(f"Create 5 accounting flashcards for {card_topic}. Format: Question / Answer.")
            st.markdown(res.text)

# --- MODE: CHAT (The Socratic Tutor) ---
else:
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Discuss {st.session_state.current_folder} with your tutor..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # The OG Personality is BACK
            sys_msg = (
                f"You are the Junior Core Accounting Tutor. Your personality is supportive and Socratic. "
                f"Current Topic: {st.session_state.current_folder}. "
                "NEVER give the final answer immediately. Ask guiding questions to lead the user to the logic. "
                "If the user shows correct reasoning, award '+10 XP'. "
                f"User says: {prompt}"
            )
            response = model.generate_content(sys_msg)
            
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
                
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
