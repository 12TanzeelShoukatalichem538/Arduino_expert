import streamlit as st
import os
import google.generativeai as genai
from google import genai
from google.genai import types


# --- Load Gemini API key from Streamlit secrets ---
api_key = st.secrets["general"]["GOOGLE_API_KEY"]

# --- Load knowledge base ---
with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# --- Chat function ---
def chat(user_input, history):
    history = history or []

    if not api_key:
        return history, "⚠️ API key not found in secrets.toml"

    if not knowledge_base:
        return history, "⚠️ Knowledge base is empty."

    # Combine knowledge base + chat history + current input
    context_text = f"Use the following knowledge base to answer the user's question:\n\n{knowledge_base}\n\n"
    context_text += "Previous chat history:\n"
    for msg in history:
        context_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context_text += f"User: {user_input}\nAnswer based on the knowledge above."

    try:
        client = genai.Client(api_key=api_key)
        chat_session = client.chats.create(model="gemini-2.5-flash")
        response = chat_session.send_message(context_text)
        reply = response.text
    except Exception as e:
        reply = f"❌ Error calling Gemini model: {e}"

    # Append new messages
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})

    return history, ""


# --- Streamlit UI ---
st.set_page_config(page_title="Arduino Expert Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Arduino Expert Chatbot")
st.markdown("Ask me anything about Arduino projects!")

# Store chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]

# Chat display
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Arduino Expert:** {msg['content']}")

# User input
user_input = st.text_input("💬 Your Question:", placeholder="Type your Arduino question here...")

if st.button("🚀 Send") and user_input:
    st.session_state.chat_history, _ = chat(user_input, st.session_state.chat_history)
    st.experimental_rerun()

if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]
    st.experimental_rerun()
