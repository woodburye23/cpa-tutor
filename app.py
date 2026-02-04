import streamlit as st
import google.generativeai as genai
import time
import json
from PyPDF2 import PdfReader

# 1. Page Config
st.set_page_config(page_title="Junior Core Master Studio", layout="wide")

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

# 3. Helper Function to Read PDFs and Text
def get_all_text(files):
    combined_text = ""
    for file in files:
        try:
            if file.name.lower().endswith('.pdf'):
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content: combined_text += content
            else:
                combined_text += file.getvalue().decode("utf-8")
        except: continue
    return combined_text[:15000]

# 4. Smart Timer Fragment
@st.fragment(run_every=1.0)
def pomodoro_timer():
    if st.session_state.sprint_end:
        remaining = st.session_state.sprint_end - time.time()
        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            st.metric("⏳ Core Focus Timer", f"{mins:02d}:{secs:02d}")
        else:
            st.session_state.sprint_end = None
            st.session_state.xp += 20
            st.balloons()
            st.success("Focus Session Complete! +20 XP")
            st.rerun()
    else:
        if st.button("🚀 Start Study Sprint"):
            st.session_state.sprint_end = time.time() + (25 * 60)
            st.rerun()

# 5. Sidebar Tools
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    st.divider()
    pomodoro_timer()
    st.divider()
    st.subheader("📁 Class Folders")
    new_folder = st.text_input("New Folder Name")
    if st.button("Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder
            st.rerun()
    st.session_state.current_folder = st.selectbox("Current Focus", list(st.session_state.folders.keys()))
    st.divider()
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Multi-Doc Quiz"): st.session_state.mode = "quiz"
    if st.button("🎮 Concept Challenge"): st.session_state.mode = "game"
    st.divider()
    uploaded_files = st.file_uploader("Upload Notes (PDF/TXT)", type=['pdf', 'txt'], accept_multiple_files=True)
    if uploaded_files:
        st.success(f"🟢 {len(uploaded_files)} Docs Grounded")

# 6. Main Content Area
st.title(f"🎓 {st.session_state.current_folder}")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: CHAT (The Focused Hybrid Tutor) ---
if st.session_state.mode == "chat":
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a specific question..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            all_notes = get_all_text(uploaded_files) if uploaded_files else "No specific notes uploaded."
            
            # The Focused Prompt Logic
            focused_prompt = f"""
            SYSTEM INSTRUCTIONS: 
            You are a focused Junior Core Accounting Tutor. 
            Stay strictly on the topic the user asks about. 
            Use the provided reference notes as your primary source.
            If the answer is not in the notes, use your general accounting knowledge.

            ### REFERENCE NOTES:
            '''
            {all_notes}
            '''

            ### USER QUESTION:
            "{prompt}"

            RESPONSE GUIDELINES:
            1. Address the User Question directly and immediately.
            2. Be concise but clear.
            3. Stay Socratic (ask a follow-up question to test their logic).
            4. Award '+10 XP' if the user's logic is correct.
            """
            
            response = model.generate_content(focused_prompt)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})

# --- MODE: MULTI-DOC QUIZ ---
elif st.session_state.mode == "quiz":
    st.header("📝 Smart Quiz Generator")
    quiz_topic = st.text_input("Quiz Topic", placeholder="e.g. Revenue Recognition")
    if st.button("Build Quiz"):
        with st.spinner("Analyzing all documents..."):
            res = model.generate_content(f"Create a 3-question quiz on {quiz_topic}. Use these notes as a source: {get_all_text(uploaded_files)}")
            st.markdown(res.text)

# --- MODE: CONCEPT CHALLENGE (Game) ---
elif st.session_state.mode == "game":
    st.header("🎮 Concept Challenge")
    if st.button("Generate Random Concept"):
        with st.spinner("Picking a concept..."):
            res = model.generate_content(f"Pick one tough accounting concept from these notes and ask the user to explain it: {get_all_text(uploaded_files)}")
            st.info(res.text)
