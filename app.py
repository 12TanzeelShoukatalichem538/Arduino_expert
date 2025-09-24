import streamlit as st
import google.generativeai as genai
import os

# ----------------------------
# Load knowledge base
# ----------------------------
with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# ----------------------------
# Configure Gemini API key (from backend/secrets)
# ----------------------------
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Create chat model
model = genai.GenerativeModel("gemini-1.5-flash")
chat_session = model.start_chat(history=[])

# ----------------------------
# Function: get Gemini response
# ----------------------------
def get_gemini_response(user_input: str, history: list) -> str:
    # Build context with knowledge base + history
    context_text = f"Use the following knowledge base to answer the user's question:\n\n{knowledge_base}\n\n"
    context_text += "Previous chat history:\n"
    for msg in history:
        context_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context_text += f"User: {user_input}\nAnswer based on the knowledge above."

    try:
        response = chat_session.send_message(context_text)
        return response.text
    except Exception as e:
        return f"❌ Error calling Gemini model: {e}"

# ----------------------------
# Streamlit Interface (unchanged)
# ----------------------------
st.set_page_config(page_title="Arduino Expert Chatbot")

st.title("🤖 Arduino Expert Chatbot")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ]

# Show chat messages
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    elif msg["role"] == "system":
        st.info(msg["content"])

# User input
user_input = st.chat_input("Ask a question")
if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get bot response
    bot_reply = get_gemini_response(user_input, st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # Show assistant message
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
