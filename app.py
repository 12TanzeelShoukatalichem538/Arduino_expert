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

# ----------------------------------------------------------------
# 1️⃣ --- API + FIREBASE SETUP ---
# ----------------------------------------------------------------
api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not api_key:
    st.error("❌ API key not found. Please add GOOGLE_API_KEY in Streamlit secrets or environment.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)

# Initialize Firebase (only once)
if "firebase_initialized" not in st.session_state:
    try:
        # ✅ Convert AttrDict to dict for Firebase
        firebase_credentials = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_credentials)

        if not firebase_admin._apps:  # ✅ only initialize once
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.get("database_url", "")
            })
        else:
            firebase_admin.get_app()  # ✅ reuse existing app

        st.session_state.firebase_initialized = True
    except Exception as e:
        st.warning(f"⚠️ Firebase initialization failed: {e}")

db = firestore.client()

# ----------------------------------------------------------------
# 2️⃣ --- EMAIL SETUP (for owner notification) ---
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# 2️⃣ --- EMAIL SETUP (for owner notification) ---
# ----------------------------------------------------------------
OWNER_EMAIL = "tanzeel.shoukat11@gmail.com"  # 👈 replace with your email
GMAIL_USER = st.secrets["gmail"]["gmail_user"]  # 👈 read Gmail user from secrets
GMAIL_APP_PASSWORD = st.secrets["gmail"]["gmail_app_password"]  # 👈 read Gmail App Password from secrets

def send_owner_email(subject, body):
    """Send email to owner when new chat starts"""
    try:
        if not GMAIL_USER or not GMAIL_APP_PASSWORD:
            st.warning("⚠️ Gmail credentials missing in Streamlit secrets.")
            return

        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = OWNER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com",  465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        st.error(f"❌ Email sending failed: {e}")

# OWNER_EMAIL = "tanzeel.shoukat11@gmail.com"  # 👈 replace with your email
# GMAIL_USER = "tanzeel.shoukat11@gmail.com"  # 👈 Gmail that will send notifications
# GMAIL_APP_PASSWORD = st.secrets.get("gmail_app_password")  # store in Streamlit secrets

# def send_owner_email(subject, body):
#     """Send email to owner when new chat starts"""
#     try:
#         if not GMAIL_APP_PASSWORD:
#             st.warning("⚠️ Gmail App Password missing in secrets.")
#             return
#         msg = MIMEMultipart()
#         msg["From"] = GMAIL_USER
#         msg["To"] = OWNER_EMAIL
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
#             server.send_message(msg)
#         print("✅ Email sent successfully.")
#     except Exception as e:
#         print(f"❌ Email sending failed: {e}")

# ----------------------------------------------------------------
# 3️⃣ --- SESSION HANDLING ---
# ----------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chat_started = False  # For email notification

# ----------------------------------------------------------------
# 4️⃣ --- CHAT STORAGE IN FIRESTORE ---
# ----------------------------------------------------------------
def log_message(role, text):
    """Save each message to Firestore"""
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
# 5️⃣ --- LOAD KNOWLEDGE BASE ---
# ----------------------------------------------------------------
@st.cache_data
def load_knowledge_base(file_path="knowledge.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

knowledge_base = load_knowledge_base()

# ----------------------------------------------------------------
# 6️⃣ --- RESPONSE GENERATION ---
# ----------------------------------------------------------------
def generate_response(user_query):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Answer the question based on the following knowledge:\n\n{knowledge_base}\n\nQuestion: {user_query}"
    response = model.generate_content(prompt)
    return response.text

# ----------------------------------------------------------------
# 7️⃣ --- PAGE UI (unchanged) ---
# ----------------------------------------------------------------
st.set_page_config(page_title="Arduino Expert", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    .title-container {
        background: linear-gradient(90deg, #ff6a00, #ee0979);
        padding: 20px; border-radius: 12px; text-align: center;
        margin-bottom: 25px; box-shadow: 0 0 20px #ff6a00;
    }
    .title-container h1 {color: white; font-size: 38px; font-weight: bold; margin: 0;}
    .chat-box {border-radius: 12px; padding: 12px 18px; margin: 8px 0; font-size: 16px; line-height: 1.5;
               box-shadow: 0 0 10px rgba(255,255,255,0.1);}
    .chat-user {background: linear-gradient(90deg, #4facfe, #00f2fe); color: black; font-weight: bold;}
    .chat-assistant {background: linear-gradient(90deg, #43e97b, #38f9d7); color: black;}
    .chat-system {background: linear-gradient(90deg, #ff9a9e, #fad0c4); color: black; font-style: italic;}
    .stButton>button {
        background: linear-gradient(90deg, #ee0979, #ff6a00);
        color: white; font-weight: bold; border-radius: 10px; padding: 10px 20px; border: none;
        box-shadow: 0 0 15px rgba(255,106,0,0.7);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-container'><h1>🤖 Arduino Expert Chatbot</h1></div>", unsafe_allow_html=True)

# --- Initial Chat Message ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]

# Display chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-box chat-user'>👩‍💻 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='chat-box chat-assistant'>🤖 <b>Assistant:</b> {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "system":
        st.markdown(f"<div class='chat-box chat-system'>ℹ️ {msg['content']}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 8️⃣ --- CHAT INPUT + LOGGING + NOTIFICATION ---
# ----------------------------------------------------------------
user_input = st.chat_input("💬 Ask your Arduino question...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    log_message("user", user_input)

    if not st.session_state.chat_started:
        send_owner_email(
            subject="📩 New Chat Started on Arduino Chatbot",
            body=f"A user started a chat at {datetime.utcnow()}.\n\nFirst message:\n{user_input}\n\nSession ID: {st.session_state.session_id}"
        )
        st.session_state.chat_started = True

    reply = generate_response(user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    log_message("assistant", reply)

    st.markdown(f"<div class='chat-box chat-assistant'>🤖 <b>Assistant:</b> {reply}</div>", unsafe_allow_html=True)
    if st.button("✉️ Test Email"):
         send_owner_email("Test Email", "Your chatbot email system is working!")
