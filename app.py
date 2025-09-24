import gradio as gr
import os
from google import genai
from google.genai import types

# --- Load API key from secrets.toml ---
# On Streamlit Cloud or local with secrets, the API key is stored like this:
# [general]
# GOOGLE_API_KEY = "your_api_key_here"
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in secrets.toml")

# --- Load knowledge base from repo at startup ---
with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# --- Chat function ---
def chat(user_input, history):
    global knowledge_base, api_key
    history = history or []

    if not api_key:
        return history, "⚠️ API key not set. Please configure secrets.toml."

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

    # Append messages in new Gradio format
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})

    return history, ""  # "" clears the user input box


# --- Custom CSS for Arduino Expert Theme ---
custom_css = """
.gradio-container {
    background-color: #000000 !important;  /* Black background */
    font-family: 'Arial', sans-serif;
    color: white;
    padding: 20px;
}
/* Header */
h1, h2, h3, .gr-markdown {
    color: #0082C9 !important; /* Arduino Blue */
    text-align: center;
    font-weight: bold;
}
/* Buttons */
button {
    background-color: #0082C9 !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    border: none !important;
    padding: 8px 16px !important;
}
button:hover {
    background-color: #006fa8 !important;
}
/* Textboxes */
textarea, input {
    border: 2px solid #0082C9 !important;
    border-radius: 6px !important;
    background-color: #1a1a1a !important;
    color: white !important;
}
/* Chatbot */
.gr-chatbot {
    border: 2px solid #0082C9 !important;
    border-radius: 10px !important;
    background-color: #ffffff !important; /* White chat background */
    color: black !important;
    max-height: 65vh !important; 
    overflow-y: auto !important;
}
"""

# --- Gradio UI ---
with gr.Blocks(css=custom_css, theme="soft") as demo:
    gr.Markdown("## 🤖 Arduino Expert Chatbot")

    # Store chat history in session with initial greeting
    chat_history = gr.State([
        {"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}
    ])

    # Chatbot interface
    chatbot = gr.Chatbot(type="messages", label="Conversation", height=500)
    user_input = gr.Textbox(label="💬 Ask a question", placeholder="Type your Arduino question here...")
    
    with gr.Row():
        send_btn = gr.Button("🚀 Send")
        clear_btn = gr.Button("🗑️ Clear Chat")

    # Send message
    send_btn.click(fn=chat, inputs=[user_input, chat_history], outputs=[chatbot, user_input])
    user_input.submit(fn=chat, inputs=[user_input, chat_history], outputs=[chatbot, user_input])

    # Clear chat
    clear_btn.click(
        lambda: [{"role": "system", "content": "👋 Welcome to Arduino Expert! Ask me anything about Arduino projects."}],
        None,
        chatbot
    )

demo.launch(share=True)
