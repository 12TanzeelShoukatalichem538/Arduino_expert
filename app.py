import streamlit as st
import google.generativeai as genai

# ✅ Configure Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- Load knowledge base ---
with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# --- Chat function ---
def chat_with_gemini(user_input, history):
    if not knowledge_base:
        return "⚠️ Knowledge base is empty."

    # Build context with knowledge + chat history
    context_text = f"Use the following knowledge base to answer the user's question:\n\n{knowledge_base}\n\n"
    context_text += "Previous chat history:\n"
    for msg in history:
        context_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context_text += f"User: {user_input}\nAnswer based on the knowledge above."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(context_text)
        reply = response.text
    except Exception as e:
        reply = f"❌ Error calling Gemini model: {e}"

    return reply


# --- Streamlit Page Config ---
st.set_page_config(page_title="Arduino Expert", page_icon="🤖", layout="centered")

# --- Custom CSS (Dark + Neon Style) ---
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .title-container {
        background: linear-gradient(90deg, #ff6a00, #ee0979);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 0 20px #ff6a00;
    }
    .title-container h1 {
        color: white;
        font-size: 38px;
        font-weight: bold;
        margin: 0;
    }
    .chat-box {
        border-radius: 12px;
        padding: 12px 18px;
        margin: 8px 0;
        font-size: 16px;
        line-height: 1.5;
        box-shadow: 0 0 10px rgba(255,255,255,0.1);
    }
    .chat-user {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        color: black;
        font-weight: bold;
    }
    .chat-assistant {
        background: linear-gradient(90deg, #43e97b, #38f9d7);
        color: black;
    }
    .chat-system {
        background: linear-gradient(90deg, #ff9a9e, #fad0c4);
        color: black;
        font-style: italic;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ee0979, #ff6a00);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 0 15px rgba(255,106,0,0.7);
    }
    </style>
""", unsafe_allow_html=True)


# --- Title Section ---
st.markdown("<div class='title-container'><h1>🤖 Arduino Expert Chatbot</h1></div>", unsafe_allow_html=True)

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]

# --- Chat Window ---
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-box chat-user'>🙋 {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='chat-box chat-assistant'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "system":
        st.markdown(f"<div class='chat-box chat-system'>{msg['content']}</div>", unsafe_allow_html=True)

# --- User Input ---
if prompt := st.chat_input("Ask your Arduino question..."):
    # User message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.markdown(f"<div class='chat-box chat-user'>🙋 {prompt}</div>", unsafe_allow_html=True)

    # Gemini response
    reply = chat_with_gemini(prompt, st.session_state["messages"])
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.markdown(f"<div class='chat-box chat-assistant'>🤖 {reply}</div>", unsafe_allow_html=True)

# --- Clear Chat Button ---
if st.button("🧹 Clear Chat"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]
    st.experimental_rerun()
