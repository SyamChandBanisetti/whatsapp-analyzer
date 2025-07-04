import streamlit as st
from google.generativeai import GenerativeModel, configure
import os

# 🔐 Configure Gemini API
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")
st.title("📲 WhatsApp Chat Analyzer")

# Step 1: Upload WhatsApp chat file
uploaded_file = st.file_uploader("📁 Upload WhatsApp Chat (.txt)", type=["txt"])

chat_text = ""
if uploaded_file:
    chat_text = uploaded_file.read().decode("utf-8")
    st.success("✅ Chat file uploaded!")

# Step 2: Analyze using Gemini
if chat_text and st.button("📊 Analyze Important Info"):
    prompt = f"""
From the following WhatsApp chat log, extract:
- 📌 Key messages or announcements
- 🕒 Dates, schedules, meetings
- 🔗 Links shared
- ✅ Action items or tasks

Return in markdown with sections:
1. Summary
2. Links
3. Schedules
4. Tasks

Chat content:
{chat_text}
"""
    with st.spinner("Analyzing chat with Gemini..."):
        response = model.generate_content(prompt)
        st.markdown("### 📊 Analysis Result")
        st.markdown(response.text)

# Step 3: Chatbot interface
if chat_text:
    st.markdown("---")
    st.subheader("🤖 Chat with Your WhatsApp Data")

    user_input = st.text_input("Ask a question (e.g., What meetings are planned?)")
    if user_input:
        chat_prompt = f"""
You are an AI assistant. Use the WhatsApp chat log below to answer the user's question.

User's question:
{user_input}

Chat content:
{chat_text}
"""
        with st.spinner("Thinking..."):
            chat_response = model.generate_content(chat_prompt)
            st.markdown("**Response:**")
            st.markdown(chat_response.text)
