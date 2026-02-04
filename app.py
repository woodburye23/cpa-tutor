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

# 3. Helper Function
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

# 4. Timer Fragment
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
    st.subheader("📁 Folders")
    new_folder = st.text_input("New Folder")
    if st.button("Create") and new_folder:
        st.session_state.folders[new_folder] = []
        st.session_state.current_folder = new_folder
        st.rerun()
    st.session_state.current_folder = st.selectbox("Focus", list(st.session_state.folders.keys()))
    st.divider()
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Multi-Doc Quiz"): st.session_state.mode = "quiz"
    if st.button("🎮 Concept Challenge"): st.session_state.mode = "game"
    st.divider()
    uploaded_files = st.file_uploader("Upload Notes (PDF/TXT)", type=['pdf', 'txt'], accept_multiple_files=True)

# 6. Main Content Area
st.title(f"🎓 {st.session_state.current_folder}")

if not model:
    st.error("AI connection failed.")
    st.stop()

# --- MODE: CHAT (The Hybrid Tutor) ---
if st.session_state.mode == "chat":
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # HYBRID LOGIC: If files exist, use them as 'Priority Knowledge'
            all_notes = get_all_text(uploaded_files) if uploaded_files else "No specific notes uploaded yet."
            
            sys_msg = (
                f"You are a helpful Socratic Accounting Tutor. "
                f"PRIORITY NOTES: {all_notes}\n\n"
                "INSTRUCTION: Answer the user's question. If the answer is in the PRIORITY NOTES, "
                "use that wording. If it is NOT in the notes, use your general knowledge to explain "
                "the concept clearly. Always be Socratic (ask questions) and award '+10 XP' for logic. "
                f"User Question: {prompt}"
            )
            
            response = model.generate_content(sys_msg)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})

# --- MODES: QUIZ & GAME ---
elif st.session_state.mode == "quiz":
    st.header("📝 Smart Quiz Gen")
    quiz_topic = st.text_input("Topic")
    if st.button("Build Quiz"):
        res = model.generate_content(f"Create a quiz on {quiz_topic}. Use these notes if relevant: {get_all_text(uploaded_files)}")
        st.markdown(res.text)

elif st.session_state.mode == "game":
    st.header("🎮 Concept Challenge")
    if st.button("Generate Concept"):
        res = model.generate_content(f"Ask me a hard accounting question from these notes: {get_all_text(uploaded_files)}")
        st.info(res.text)
