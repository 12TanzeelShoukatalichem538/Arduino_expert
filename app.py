import streamlit as st
import os
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading  # for async email

# ----------------------------------------------------------------
# 0️⃣ --- SAFE SESSION STATE INITIALIZATION ---
# ----------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome! How can we help you today?"}
    ]

if "cache" not in st.session_state:
    st.session_state.cache = {}

# ----------------------------------------------------------------
# 1️⃣ --- API + FIREBASE SETUP ---
# ----------------------------------------------------------------
api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not api_key:
    st.error("❌ API key not found. Please add GOOGLE_API_KEY in Streamlit secrets or environment.")
    st.stop()

genai.configure(api_key=api_key)

if "firebase_initialized" not in st.session_state:
    try:
        firebase_credentials = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_credentials)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.get("database_url", "")
            })
        else:
            firebase_admin.get_app()

        st.session_state.firebase_initialized = True
    except Exception as e:
        st.warning(f"⚠️ Firebase initialization failed: {e}")

db = firestore.client()

# ----------------------------------------------------------------
# 2️⃣ --- EMAIL SETUP ---
# ----------------------------------------------------------------
OWNER_EMAIL = "arduinotutors03@gmail.com"
GMAIL_USER = st.secrets["gmail"]["gmail_user"]
GMAIL_APP_PASSWORD = st.secrets["gmail"]["gmail_app_password"]

def send_owner_email(subject, body):
    """Send email in background to avoid blocking"""
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = OWNER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

# ----------------------------------------------------------------
# 3️⃣ --- CHAT STORAGE ---
# ----------------------------------------------------------------
def log_message(role, text):
    try:
        chat_ref = db.collection("chats").document(st.session_state.session_id)
        chat_ref.collection("messages").add({
            "role": role,
            "text": text,
            "timestamp": datetime.utcnow()
        })
        chat_ref.set({
            "meta": {
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            }
        }, merge=True)
    except Exception as e:
        print(f"❌ Firestore logging error: {e}")

# ----------------------------------------------------------------
# 4️⃣ --- LOAD KNOWLEDGE BASE ---
# ----------------------------------------------------------------
@st.cache_data
def load_knowledge_base(file_path="knowledge.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

knowledge_base = load_knowledge_base()

# ----------------------------------------------------------------
# 5️⃣ --- RESPONSE GENERATION WITH TRUNCATION + STREAMING ---
# ----------------------------------------------------------------
def get_relevant_knowledge(user_query, kb, limit=1500):
    """Take first 1500 chars as context"""
    return kb[:limit]

def generate_response(user_query):
    model = genai.GenerativeModel("gemini-2.5-flash")
    context = get_relevant_knowledge(user_query, knowledge_base)

    prompt = f"""
You are a friendly Arduino expert chatting like a human.

Use this knowledge if relevant:
{context}

User question:
{user_query}

Answer in a natural, human-like tone.
"""

    # Streaming response
    response = model.generate_content(prompt, stream=True)
    final_text = ""
    for chunk in response:
        if chunk.text:
            final_text += chunk.text
    return final_text.strip()

# ----------------------------------------------------------------
# 6️⃣ --- PAGE UI ---
# ----------------------------------------------------------------
st.set_page_config(page_title="Chat With Us", page_icon="💬", layout="wide")

st.markdown("""
<style>
body {background-color: #0e1117; color: white;}

.title-container {
    background: linear-gradient(90deg, #ff6a00, #ee0979);
    padding: 8px 12px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 15px;
}

.title-container h1 {
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin: 0;
}

.chat-box {
    border-radius: 12px;
    padding: 12px 18px;
    margin: 8px 0;
    font-size: 16px;
    line-height: 1.5;
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
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-container'><h1>Chat With Us</h1></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 7️⃣ --- DISPLAY CHAT HISTORY ---
# ----------------------------------------------------------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-box chat-user'>👩‍💻 {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='chat-box chat-assistant'>{msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "system":
        st.markdown(f"<div class='chat-box chat-system'>{msg['content']}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 8️⃣ --- CHAT INPUT + LOGGING + ASYNC EMAIL ---
# ----------------------------------------------------------------
user_input = st.chat_input("💬 Type your message...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    log_message("user", user_input)

    # Async email sending
    if not st.session_state.chat_started:
        subject = "📩 New Chat Started"
        body = f"First message:\n{user_input}\n\nSession ID: {st.session_state.session_id}"
        threading.Thread(target=send_owner_email, args=(subject, body)).start()
        st.session_state.chat_started = True

    # Check cache
    if user_input in st.session_state.cache:
        reply = st.session_state.cache[user_input]
    else:
        reply = generate_response(user_input)
        st.session_state.cache[user_input] = reply

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    log_message("assistant", reply)

    st.markdown(f"<div class='chat-box chat-assistant'>{reply}</div>", unsafe_allow_html=True)
