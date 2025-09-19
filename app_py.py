import streamlit as st
import google.generativeai as genai
import os

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

def chat(user_input):
    context_text = f"Knowledge base:\n{knowledge_base}\n\n"
    for msg in st.session_state.chat_history:
        context_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context_text += f"User: {user_input}\nAnswer based ONLY on the knowledge base above."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(context_text)
        reply = response.text
    except Exception as e:
        reply = f"❌ Error: {e}"

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    return reply

# --- Streamlit Page Config ---
st.set_page_config(page_title="Arduino Expert", page_icon="🤖", layout="centered")

# --- Custom UI ---
st.markdown(
    """
    <style>
    .main {background-color: #f8f9fa;}
    h1 {
        color: white;
        background-color: black;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1>🤖 Arduino Expert Chatbot</h1>", unsafe_allow_html=True)

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
    st.experimental_rerun()
