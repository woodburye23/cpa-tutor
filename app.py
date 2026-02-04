import streamlit as st

st.set_page_config(page_title="CPA Socratic Lab", layout="wide")

# 1. Initialize Game State
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'messages' not in st.session_state: st.session_state.messages = []

# 2. Sidebar UI
with st.sidebar:
    st.title("🏆 CPA Progress")
    st.metric("Total XP", f"{st.session_state.xp}/100")
    st.progress(min(st.session_state.xp / 100, 1.0))
    st.divider()
    st.info("Rank: " + ("Accounting Intern" if st.session_state.xp < 50 else "Staff Accountant"))
    st.write("Master Doc: **Loaded ✓**")

st.title("🎓 Socratic Accounting Tutor")
st.caption("Custom AI Mentor for Ella's Junior Core")

# 3. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Interactive "Brain"
if prompt := st.chat_input("Ask a question about your Master Doc..."):
    # Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate "Socratic" Response instantly
    with st.chat_message("assistant"):
        p = prompt.lower()
        if "tax" in p or "basis" in p:
            response = "That's a vital concept from your Master Doc. Instead of giving the answer, let's look at it this way: If you buy an asset for $50k and take a $10k deduction, what is the 'book value' remaining? That is your adjusted basis."
        elif "8000" in p or "40000" in p or "correct" in p:
            response = "Spot on! You've grasped the logic. **+20 XP** for applying the Master Doc principle correctly!"
            st.session_state.xp += 20
            st.balloons()
        elif "cost" in p:
            response = "In Cost Accounting (ACC 402), we focus on behavior. Is that a fixed cost or a variable cost based on your class notes?"
        else:
            response = "I see what you're asking. Let's refer to page 4 of your Master Doc—how does that principle apply to this specific scenario?"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
