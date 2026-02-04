import streamlit as st
import google.generativeai as genai
import time
import json

# 1. Page Config
st.set_page_config(page_title="Junior Core Study OS", layout="wide")

# Initialize Session States
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: st.session_state.folders = {"General": []}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "General"
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

# 3. The 2026 "Smart Timer" (Updates every second automatically)
@st.fragment(run_every=1.0)
def pomodoro_timer():
    if st.session_state.sprint_end:
        remaining = st.session_state.sprint_end - time.time()
        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            st.metric("⏳ Deep Work Timer", f"{mins:02d}:{secs:02d}")
        else:
            st.session_state.sprint_end = None
            st.session_state.xp += 20
            st.balloons()
            st.success("Sprint Over! +20 XP")
            st.rerun()
    else:
        if st.button("🚀 Start 25m Sprint"):
            st.session_state.sprint_end = time.time() + (25 * 60)
            st.rerun()

# 4. Sidebar: The Command Center
with st.sidebar:
    st.title(f"🏆 {st.session_state.xp} XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    pomodoro_timer()  # Calling the smart timer here

    st.divider()
    st.subheader("📂 Topic Folders")
    new_folder = st.text_input("New Topic Name", placeholder="e.g. Tax Basis")
    if st.button("Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder
            st.rerun()

    st.session_state.current_folder = st.selectbox("Current Topic", list(st.session_state.folders.keys()))

    st.divider()
    # Navigation Modes
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Chat"): st.session_state.mode = "chat"
        if st.button("📝 Quiz"): st.session_state.mode = "quiz"
    with col2:
        if st.button("🗂️ Cards"): st.session_state.mode = "flashcards"
        if st.button("🧹 Clear"): 
            st.session_state.folders[st.session_state.current_folder] = []
            st.rerun()

    # Download History
    st.divider()
    chat_data = json.dumps(st.session_state.folders[st.session_state.current_folder], indent=2)
    st.download_button(label="📥 Save Study Log", data=chat_data, file_name=f"{st.session_state.current_folder}_log.json")

# 5. Main Content Area
st.title(f"🎓 {st.session_state.current_folder} Master Studio")

if not model:
    st.error("AI connection failed. Check your API key!")
    st.stop()

# --- MODES ---
if st.session_state.mode == "quiz":
    st.header("📝 CPA Practice Quiz")
    if st.button("Generate Questions"):
        with st.spinner("AI is thinking..."):
            res = model.generate_content(f"Generate 3 CPA-style multiple choice questions for {st.session_state.current_folder}.")
            st.markdown(res.text)

elif st.session_state.mode == "flashcards":
    st.header("🗂️ Active Recall Cards")
    if st.button("Generate Cards"):
        with st.spinner("Thinking..."):
            res = model.generate_content(f"Create 3 flashcards for {st.session_state.current_folder}.")
            st.markdown(res.text)

else: # Chat Mode
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask about {st.session_state.current_folder}..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"You are a Socratic Accounting Tutor for {st.session_state.current_folder}. Award +10 XP for correct reasoning. Prompt: {prompt}"
            response = model.generate_content(context)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
