import streamlit as st
import requests

# ✅ OpenRouter API Key
import os
API_KEY = os.environ.get("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")


# ✅ Detect if query is in Hinglish
def detect_hinglish(text):
    keywords = [
        "kya", "hai", "karu", "karna", "divorce", "patni", "shaadi", "notice", "maintenance",
        "kab", "mujhe", "mere", "kyunki", "kyon", "case", "ladki", "biwi", "court", "file", "dono"
    ]
    return any(word in text.lower() for word in keywords)

# ✅ Call OpenRouter API
def ask_openrouter(messages, force_hinglish=False):
    system_prompt = (
        "You are LawGuide, a legal expert for Indian laws. Reply only in Hinglish (Hindi written in English letters). Use simple language, avoid English sentences."
        if force_hinglish else
        "You are LawGuide, a legal assistant trained on Indian law. Help users with IPC, CrPC, family law, legal drafts, and case law. Respond in clear English."
    )

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "system", "content": system_prompt}] + messages
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://lawguide.streamlit.app",  # Must be included
        "X-Title": "LawGuide"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {e}"

# ✅ Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "history_titles" not in st.session_state:
    st.session_state.history_titles = []
if "current_title" not in st.session_state:
    st.session_state.current_title = "New Chat"

# ✅ Sidebar: Chat history
st.sidebar.title("📂 Chat History")
if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_history = []
    st.session_state.current_title = "New Chat"

# Show chat titles
for title in st.session_state.history_titles:
    if st.sidebar.button(f"📝 {title}"):
        st.session_state.current_title = title
        st.session_state.chat_history = st.session_state.history_titles[title]

# ✅ App Title
st.title("⚖️ LawGuide – Indian Legal AI")
st.markdown("Get legal help with Indian law in Hinglish or English. Ask about IPC, CrPC, family law, and more.")

# ✅ Input box
user_query = st.chat_input("💬 Ask your legal question here...")

# ✅ Handle message
if user_query:
    force_hinglish = detect_hinglish(user_query)

    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # Get AI response
    with st.spinner("🧠 Thinking..."):
        response = ask_openrouter(st.session_state.chat_history, force_hinglish)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Save to title history if first message
    if st.session_state.current_title == "New Chat":
        title = user_query[:30] + "..." if len(user_query) > 30 else user_query
        st.session_state.current_title = title
        st.session_state.history_titles.append(title)

# ✅ Display chat messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
