import streamlit as st
import google.generativeai as genai
import time
from PyPDF2 import PdfReader

# 1. Page Config
st.set_page_config(page_title="Junior Core Master Studio", layout="wide")

# --- 2. BULLETPROOF INITIALIZATION ---
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: 
    st.session_state.folders = {"General": {"messages": [], "files": []}}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "General"
if 'mode' not in st.session_state: st.session_state.mode = "chat"
if 'sprint_end' not in st.session_state: st.session_state.sprint_end = None

# Safety Check: If the app loads an old folder structure, reset it to the new one
for f_name in list(st.session_state.folders.keys()):
    if not isinstance(st.session_state.folders[f_name], dict) or 'messages' not in st.session_state.folders[f_name]:
        st.session_state.folders[f_name] = {"messages": [], "files": []}

# 3. AI Connection Logic
@st.cache_resource
def init_ai():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-3-flash-preview')
    except: return None

model = init_ai()

# 4. Helper Function: Process Folder-Specific Files
def process_folder_files(file_objects):
    combined_text = ""
    for file in file_objects:
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

# 5. Smart Timer Fragment
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

# 6. Sidebar: The Folder & Storage System
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    st.divider()
    pomodoro_timer()
    st.divider()
    
    st.subheader("📁 Class Folders")
    new_folder_name = st.text_input("Create New Folder", placeholder="e.g. Audit")
    if st.button("Create") and new_folder_name:
        if new_folder_name not in st.session_state.folders:
            st.session_state.folders[new_folder_name] = {"messages": [], "files": []}
            st.session_state.current_folder = new_folder_name
            st.rerun()

    st.session_state.current_folder = st.selectbox("Switch Folder", list(st.session_state.folders.keys()))
    
    st.divider()
    # FOLDER-SPECIFIC UPLOADER
    st.subheader(f"📥 Folder Storage: {st.session_state.current_folder}")
    uploaded = st.file_uploader("Upload to this folder", type=['pdf', 'txt'], accept_multiple_files=True, key=f"uploader_{st.session_state.current_folder}")
    
    if uploaded:
        st.session_state.folders[st.session_state.current_folder]['files'] = uploaded
        st.success(f"Grounded in {len(uploaded)} files.")

    st.divider()
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Topic Quiz"): st.session_state.mode = "quiz"
    if st.button("🎮 Challenge Mode"): st.session_state.mode = "game"

# 7. Main Content Area
st.title(f"📂 {st.session_state.current_folder} Studio")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: CHAT (Focused on Folder Data) ---
if st.session_state.mode == "chat":
    for msg in st.session_state.folders[st.session_state.current_folder]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Discuss {st.session_state.current_folder}..."):
        st.session_state.folders[st.session_state.current_folder]['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            current_notes = process_folder_files(st.session_state.folders[st.session_state.current_folder]['files'])
            
            focused_prompt = f"""
            SYSTEM: You are a Junior Core Accounting Tutor. Stay on topic.
            FOLDER CONTEXT: {st.session_state.current_folder}
            REFERENCE MATERIAL: '''{current_notes}'''
            
            USER QUESTION: "{prompt}"
            
            INSTRUCTIONS: Answer the user's question directly. 
            Prioritize the REFERENCE MATERIAL for facts. 
            If the answer isn't there, use general accounting knowledge.
            Be Socratic, ask a follow-up, and award '+10 XP' for logic.
            """
            
            response = model.generate_content(focused_prompt)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder]['messages'].append({"role": "assistant", "content": response.text})

# --- MODE: QUIZ & GAME ---
elif st.session_state.mode == "quiz":
    st.header(f"📝 {st.session_state.current_folder} Quiz")
    if st.button("Build Quiz from Folder Notes"):
        notes = process_folder_files(st.session_state.folders[st.session_state.current_folder]['files'])
        res = model.generate_content(f"Create a 3-question quiz based on these notes: {notes}")
        st.markdown(res.text)

elif st.session_state.mode == "game":
    st.header("🎮 Concept Challenge")
    if st.button("Generate Concept"):
        notes = process_folder_files(st.session_state.folders[st.session_state.current_folder]['files'])
        res = model.generate_content(f"Pick a concept from the folder notes: {notes}")
        st.info(res.text)
