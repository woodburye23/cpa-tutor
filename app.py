import streamlit as st
import google.generativeai as genai
import time
import json

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

# 3. Smart Timer Fragment
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

# 4. Sidebar Tools
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    pomodoro_timer()

    st.divider()
    st.subheader("📁 Class Folders")
    new_folder = st.text_input("New Class/Topic", placeholder="e.g. Audit, Tax, Finance")
    if st.button("Create Folder") and new_folder:
        st.session_state.folders[new_folder] = []
        st.session_state.current_folder = new_folder
        st.rerun()

    st.session_state.current_folder = st.selectbox("Current Focus", list(st.session_state.folders.keys()))

    st.divider()
    if st.button("💬 Socratic Tutor"): st.session_state.mode = "chat"
    if st.button("📝 Master Doc Quiz"): st.session_state.mode = "quiz"
    if st.button("🎮 Junior Core Challenge"): st.session_state.mode = "game"
    
    st.divider()
    uploaded_file = st.file_uploader("Upload Master Doc / Quizlet Export", type=['pdf', 'txt'])
    if uploaded_file:
        st.success("🟢 Document Grounding Active")
    else:
        st.warning("🟡 Using General Knowledge")

# 5. Main Content Area
st.title(f"🎓 Junior Core: {st.session_state.current_folder}")

# --- MODE: GAME (QUIZLET STYLE) ---
if st.session_state.mode == "game":
    st.header("🎮 Concept Challenge")
    st.write("I'll pull a tough concept from your notes—you explain the logic!")
    if st.button("Generate Concept"):
        with st.spinner("Scanning notes..."):
            context = "Pick a specific, difficult accounting concept from these notes and ask the user to explain it. "
            if uploaded_file:
                # Read file for the game
                file_content = uploaded_file.getvalue().decode("utf-8")[:3000]
                context += f"Source Material: {file_content}"
            res = model.generate_content(context)
            st.info(res.text)

# --- MODE: CUSTOM QUIZ ---
elif st.session_state.mode == "quiz":
    st.header("📝 Custom Quiz Generator")
    quiz_topic = st.text_input("What should the quiz focus on?", placeholder="e.g. 5 questions on Deferred Tax Assets")
    if st.button("Build Quiz"):
        with st.spinner("Analyzing..."):
            prompt = f"Create a quiz on {quiz_topic}. "
            if uploaded_file:
                file_content = uploaded_file.getvalue().decode("utf-8")[:4000]
                prompt += f"STRICTLY use ONLY these notes: {file_content}"
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
            doc_context = ""
            if uploaded_file:
                # Grounding the chat in the file
                file_content = uploaded_file.getvalue().decode("utf-8")[:4000]
                doc_context = f"STRICT SOURCE MATERIAL: {file_content}. "
            
            sys_msg = (
                f"You are the Junior Core Accounting Tutor. {doc_context} "
                "Socratic Method: NEVER give direct answers. Guide the student through the logic. "
                "If the student shows correct reasoning based on the source, award '+10 XP'. "
                f"User: {prompt}"
            )
            response = model.generate_content(sys_msg)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
