import streamlit as st
import google.generativeai as genai
import time

# 1. Page Config
st.set_page_config(page_title="Junior Core Study OS", layout="wide")

# Initialize Session States
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: st.session_state.folders = {"General": []}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "General"
if 'flashcards' not in st.session_state: st.session_state.flashcards = []

# 2. Connection Logic
@st.cache_resource
def init_ai():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-3-flash-preview')
    except: return None

model = init_ai()

# 3. Sidebar: The Command Center
with st.sidebar:
    st.title("🏆 CPA Progress: " + str(st.session_state.xp) + " XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    # Feature 1: Pomodoro Timer
    st.subheader("⏱️ Focus Timer")
    if st.button("Start 25m Sprint"):
        with st.empty():
            for seconds in range(25 * 60, 0, -1):
                mins, secs = divmod(seconds, 60)
                st.metric("Time Left", f"{mins:02d}:{secs:02d}")
                time.sleep(1)
            st.success("Sprint Over! +20 XP")
            st.session_state.xp += 20

    st.divider()
    st.subheader("📂 Topic Folders")
    new_folder = st.text_input("New Topic Name")
    if st.button("Create Folder") and new_folder:
        st.session_state.folders[new_folder] = []
        st.session_state.current_folder = new_folder

    st.session_state.current_folder = st.selectbox("Topic", list(st.session_state.folders.keys()))

    st.divider()
    if st.button("🎯 Generate Practice Quiz"):
        st.session_state.mode = "quiz"
    if st.button("🗂️ Generate Flashcards"):
        st.session_state.mode = "flashcards"
    if st.button("💬 Back to Chat"):
        st.session_state.mode = "chat"

# 4. Main Interface Logic
st.title(f"🎓 {st.session_state.current_folder} Master Studio")

if getattr(st.session_state, 'mode', 'chat') == "quiz":
    st.header("📝 Personalized CPA Quiz")
    if st.button("Run Generator"):
        res = model.generate_content("Generate 3 hard CPA questions about " + st.session_state.current_folder)
        st.write(res.text)

elif st.session_state.mode == "flashcards":
    st.header("🗂️ Active Recall Cards")
    # This turns the last 2 chat messages into a card
    if st.button("Generate Cards from Chat"):
        res = model.generate_content("Create 3 flashcards (Question/Answer) from this topic: " + st.session_state.current_folder)
        st.write(res.text)

else:
    # --- Standard Chat Mode ---
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a Socratic question..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            response = model.generate_content("You are a Socratic Accounting Tutor. If the user is right, say '+10 XP'. Topic: " + st.session_state.current_folder + " Prompt: " + prompt)
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
