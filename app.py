import streamlit as st
import google.generativeai as genai
import time
import json
from PyPDF2 import PdfReader # Required for PDF support

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

# 3. Helper Function to Read Multiple File Types
def get_all_text(files):
    combined_text = ""
    for file in files:
        try:
            combined_text += f"\n--- Source: {file.name} ---\n"
            if file.name.lower().endswith('.pdf'):
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content:
                        combined_text += content
            else:
                combined_text += file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
    return combined_text[:15000] # Increased limit for multi-doc support

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
    new_folder = st.text_input("New Folder Name", placeholder="e.g. Tax, Audit")
    if st.button("Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder
            st.rerun()

    st.session_state.current_folder = st.selectbox("Current Focus", list(st.session_state.folders.keys()))

    st.divider()
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Multi-Doc Quiz"): st.session_state.mode = "quiz"
    if st.button("🎮 Junior Core Challenge"): st.session_state.mode = "game"
    
    st.divider()
    uploaded_files = st.file_uploader("Upload Master Docs / Quizlets / Syllabus", type=['pdf', 'txt'], accept_multiple_files=True)
    if uploaded_files:
        st.success(f"🟢 {len(uploaded_files)} Documents Grounded")
    else:
        st.warning("🟡 Using General Knowledge")

# 6. Main Content Area
st.title(f"🎓 Junior Core: {st.session_state.current_folder}")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: GAME ---
if st.session_state.mode == "game":
    st.header("🎮 Concept Challenge")
    if st.button("Generate Concept from My Docs"):
        with st.spinner("Scanning documents..."):
            context = "Pick a difficult accounting concept from these notes and ask the user to explain it. "
            if uploaded_files:
                context += f"Sources: {get_all_text(uploaded_files)}"
            res = model.generate_content(context)
            st.info(res.text)

# --- MODE: CUSTOM QUIZ ---
elif st.session_state.mode == "quiz":
    st.header("📝 Comprehensive Quiz Gen")
    quiz_topic = st.text_input("What should the quiz focus on?", placeholder="e.g. Mixed quiz on Syllabus + Master Doc")
    if st.button("Build Quiz"):
        with st.spinner("Analyzing all documents..."):
            prompt = f"Create a quiz on {quiz_topic}. "
            if uploaded_files:
                prompt += f"STRICTLY use ONLY these combined sources: {get_all_text(uploaded_files)}"
            res = model.generate_content(prompt)
            st.markdown(res.text)

# --- MODE: CHAT (The Socratic Tutor) ---
else:
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about the Master Doc..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            all_doc_content = ""
            if uploaded_files:
                all_doc_content = f"STRICT SOURCE MATERIAL: {get_all_text(uploaded_files)}. "
            
            sys_msg = (
                f"You are the Junior Core Accounting Tutor. {all_doc_content} "
                "Socratic Method: Lead the student. Award '+10 XP' for correct reasoning based on these specific documents."
                f"User: {prompt}"
            )
            response = model.generate_content(sys_msg)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
