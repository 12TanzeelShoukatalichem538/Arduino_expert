import streamlit as st
import os
import google.generativeai as genai

# --- Load knowledge base ---
with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# --- Configure API Key (from Streamlit Secrets) ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]

# --- Chat function (replaced with HuggingFace-style logic) ---
def chat(user_input):
    context_text = f"Use the following knowledge base to answer the user's question:\n\n{knowledge_base}\n\n"
    context_text += "Previous chat history:\n"
    for msg in st.session_state.chat_history:
        context_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context_text += f"User: {user_input}\nAnswer based on the knowledge above."

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        chat_session = client.chats.create(model="gemini-2.5-flash")
        response = chat_session.send_message(context_text)
        reply = response.text
    except Exception as e:
        reply = f"❌ Error calling Gemini model: {e}"

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
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

# --- Chat Window ---
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).markdown(msg["content"])

user_input = st.chat_input("Ask a question...")
if user_input:
    reply = chat(user_input)
    st.chat_message("assistant").markdown(reply)

if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]
    st.rerun()
