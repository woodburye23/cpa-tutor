import streamlit as st
import google.generativeai as genai

# 1. Page Config & Professional Styling
st.set_page_config(page_title="Junior Core Accounting Tutor", layout="wide")

# Initialize Session States
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'folders' not in st.session_state: st.session_state.folders = {"General": []}
if 'current_folder' not in st.session_state: st.session_state.current_folder = "General"

# 2. Connection Logic
@st.cache_resource
def init_ai():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-3-flash-preview')
    except: return None

model = init_ai()

# 3. Sidebar: Folders & Quiz Tool
with st.sidebar:
    st.title("🏆 Progress: " + str(st.session_state.xp) + " XP")
    st.progress(min(st.session_state.xp / 100, 1.0))
    
    st.divider()
    st.subheader("📂 Topic Folders")
    new_folder = st.text_input("Add New Topic (e.g., Tax, Audit)")
    if st.button("📁 Create Folder") and new_folder:
        if new_folder not in st.session_state.folders:
            st.session_state.folders[new_folder] = []
            st.session_state.current_folder = new_folder

    selected_folder = st.selectbox("Switch Topic", list(st.session_state.folders.keys()), index=list(st.session_state.folders.keys()).index(st.session_state.current_folder))
    st.session_state.current_folder = selected_folder

    st.divider()
    st.subheader("📝 Master Doc Tools")
    uploaded_file = st.file_uploader("Upload Notes", type=['pdf', 'txt'])
    
    if st.button("🎯 Generate 5-Question Quiz"):
        st.session_state.quiz_mode = True

# 4. Main Interface
st.title(f"🎓 Junior Core: {st.session_state.current_folder}")

# --- QUIZ LOGIC ---
if 'quiz_mode' in st.session_state and st.session_state.quiz_mode:
    st.info("Generating your custom CPA-style quiz...")
    quiz_prompt = "Based on accounting principles, generate 5 multiple choice questions. Include the correct answer at the bottom."
    response = model.generate_content(quiz_prompt)
    st.write(response.text)
    if st.button("Close Quiz"):
        del st.session_state.quiz_mode
        st.rerun()

# --- CHAT LOGIC ---
else:
    # Display messages for the CURRENT folder only
    for msg in st.session_state.folders[st.session_state.current_folder]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask about {st.session_state.current_folder}..."):
        st.session_state.folders[st.session_state.current_folder].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"You are a Socratic Tutor for {st.session_state.current_folder}. Award +10 XP for logic."
            response = model.generate_content(context + prompt)
            
            if "+10 XP" in response.text:
                st.session_state.xp += 10
                st.balloons()
            
            st.markdown(response.text)
            st.session_state.folders[st.session_state.current_folder].append({"role": "assistant", "content": response.text})
