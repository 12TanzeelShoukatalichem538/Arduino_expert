import streamlit as st
import os
import google.generativeai as genai


# --- Load API key safely ---
api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    st.error("❌ API key not found. Please add GOOGLE_API_KEY in Streamlit secrets or environment.")
    st.stop()

# Configure Generative AI
genai.configure(api_key=api_key)

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]
# Load your knowledge base text file (no change in this part)
@st.cache_data
def load_knowledge_base(file_path="knowledge.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

knowledge_base = load_knowledge_base()

# Function to generate response using knowledge base + user query
def generate_response(user_query):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Answer the question based on the following knowledge:\n\n{knowledge_base}\n\nQuestion: {user_query}"
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit UI ---
# --- Page Config ---
st.set_page_config(page_title="Arduino Expert", page_icon="🤖", layout="wide")

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

# --- Chat History Display ---
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-box chat-user'>👩‍💻 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='chat-box chat-assistant'>🤖 <b>Assistant:</b> {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "system":
        st.markdown(f"<div class='chat-box chat-system'>ℹ️ {msg['content']}</div>", unsafe_allow_html=True)

# --- Input Box ---
user_input = st.chat_input("💬 Ask your Arduino question...")
if user_input:
    reply = chat(user_input)
    st.markdown(f"<div class='chat-box chat-assistant'>🤖 <b>Assistant:</b> {reply}</div>", unsafe_allow_html=True)

# --- Clear Button ---
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]
    st.experimental_rerun()
