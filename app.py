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
st.set_page_config(page_title="Knowledge Q&A App", layout="centered")
st.title("📘 Knowledge Q&A Chatbot")

# User input
user_query = st.text_input("Ask your question:")

if st.button("Get Answer"):
    if user_query.strip() == "":
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("Generating response..."):
            answer = generate_response(user_query)
            st.success("Here’s the answer:")
            st.write(answer)
