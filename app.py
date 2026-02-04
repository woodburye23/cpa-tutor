import streamlit as st

st.set_page_config(page_title="CPA Socratic Lab", layout="wide")

# Sidebar for the "Game" feel
with st.sidebar:
    st.title("🏆 CPA Progress")
    if 'xp' not in st.session_state: st.session_state.xp = 0
    
    # Progress Bar
    progress = min(st.session_state.xp / 100, 1.0)
    st.progress(progress)
    st.metric("Total XP", f"{st.session_state.xp}/100")
    
    st.divider()
    st.info("Rank: " + ("Accounting Intern" if st.session_state.xp < 50 else "Staff Accountant"))

# Main App
st.title("🎓 Socratic Accounting Tutor")
st.write("Welcome, Ella. Let's tackle your Master Doc.")

tab1, tab2 = st.tabs(["Interactive Tutor", "Study Stats"])

with tab1:
    chat_input = st.chat_input("Ask a question about Tax Basis...")
    if chat_input:
        with st.chat_message("user"):
            st.write(chat_input)
        with st.chat_message("assistant"):
            st.write("That's a great starting point. Looking at your notes, what happens to the asset's value after a depreciation deduction is taken?")
            
    # The "Demo" buttons for your presentation
    st.divider()
    st.subheader("Simulate Learning Moments")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Correct Logic (+20 XP)"):
            st.session_state.xp += 20
            st.balloons()
    with col2:
        if st.button("Reset Session"):
            st.session_state.xp = 0
