import streamlit as st
import google.generativeai as genai
import time
from PyPDF2 import PdfReader

# 1. Page Config
st.set_page_config(page_title="Junior Core Master Studio", layout="wide")

# --- INITIALIZE SESSION STATE ---
if 'xp' not in st.session_state: st.session_state.xp = 0
# Each folder now stores: {'messages': [], 'files': []}
if 'folders' not in st.session_state: 
    st.session_state.folders = {"Junior Core": {"messages": [], "files": []}}
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

# 3. Enhanced File Reader (Processes the folder-specific files)
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

# 5. Sidebar: The Folder & Storage System
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    st.divider()
    pomodoro_timer()
    st.divider()
    
    st.subheader("📁 Manage Folders")
    new_folder_name = st.text_input("Create New Class Folder")
    if st.button("Create") and new_folder_name:
        if new_folder_name not in st.session_state.folders:
            st.session_state.folders[new_folder_name] = {"messages": [], "files": []}
            st.session_state.current_folder = new_folder_name
            st.rerun()

    st.session_state.current_folder = st.selectbox("Switch Folder", list(st.session_state.folders.keys()))
    
    st.divider()
    # FOLDER-SPECIFIC UPLOADER
    st.subheader(f"📥 Upload to '{st.session_state.current_folder}'")
    uploaded = st.file_uploader("Drop notes here", type=['pdf', 'txt'], accept_multiple_files=True, key=f"uploader_{st.session_state.current_folder}")
    
    # Save the files to the specific folder's state
    if uploaded:
        st.session_state.folders[st.session_state.current_folder]['files'] = uploaded
        st.success(f"Grounded in {len(uploaded)} files.")

    st.divider()
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Topic Quiz"): st.session_state.mode = "quiz"
    if st.button("🎮 Challenge Mode"): st.session_state.mode = "game"

# 6. Main Content Area
st.title(f"📂 {st.session_state.current_folder} Studio")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODE: CHAT (Private Folder Context) ---
if st.session_state.mode == "chat":
    # Show history for CURRENT folder only
    for msg in st.session_state.folders[st.session_state.current_folder]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask about {st.session_state.current_folder}..."):
        st.session_state.folders[st.session_state.current_folder]['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # Get only the text for the current folder
            current_notes = process_folder_files(st.session_state.folders[st.session_state.current_folder]['files'])
            
            focused_prompt = f"""
            SYSTEM: You are a Junior Core Accounting Tutor. 
            FOLDER CONTEXT: {st.session_state.current_folder}
            REFERENCE MATERIAL: '''{current_notes}'''
            
            USER QUESTION: "{prompt}"
            
            INSTRUCTIONS: Answer based on the reference material provided for this specific folder. 
            If it's not there, use general knowledge but stay in the context of {st.session_state.current_folder}.
            Award +10 XP for logic. Be Socratic.
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
        res = model.generate_content(f"Create a quiz based on these {st.session_state.current_folder} notes: {notes}")
        st.markdown(res.text)

elif st.session_state.mode == "game":
    st.header("🎮 Concept Challenge")
    if st.button("Generate Concept"):
        notes = process_folder_files(st.session_state.folders[st.session_state.current_folder]['files'])
        res = model.generate_content(f"Pick a concept from the {st.session_state.current_folder} notes: {notes}")
        st.info(res.text)
