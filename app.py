import streamlit as st
from google.generativeai import GenerativeModel, configure
import os
import re
from datetime import datetime

# 🔐 Configure Gemini API
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-2.0-flash")

# 🚀 Page settings
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")
st.title("📲 WhatsApp Chat Analyzer")

# 📝 Upload step
uploaded_file = st.file_uploader("📁 Upload WhatsApp Chat (.txt)", type=["txt"])

# 🔍 Parse and sort messages by timestamp (newest to oldest)
def parse_and_sort(text):
    pattern = r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s+(\d{1,2}:\d{2})\s*(AM|PM)?\s+-"
    lines = text.splitlines()
    messages = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            date_str = match.group(1)
            time_str = match.group(2) + (" " + match.group(3) if match.group(3) else "")
            for fmt in ("%d/%m/%Y %I:%M %p", "%m/%d/%Y %I:%M %p", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"):
                try:
                    dt = datetime.strptime(f"{date_str} {time_str}", fmt)
                    messages.append((dt, line))
                    break
                except:
                    continue
    messages.sort(reverse=True)
    return "\n".join([msg[1] for msg in messages])

chat_text = ""
if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8")
    chat_text = parse_and_sort(raw_text)
    st.success("✅ Chat file uploaded and sorted (newest first).")

# 🔎 Analyze
if chat_text and st.button("📊 Analyze Important Info"):
    prompt = f"""
From the following WhatsApp chat log, extract clearly:

1. Summary of key discussions
2. All shared links
3. Dates or time-based schedules
4. Tasks or action items

Return in markdown with the following sections:
## Summary
## Links
## Schedules
## Tasks

Chat content:
{chat_text}
"""
    with st.spinner("Analyzing chat with Gemini..."):
        response = model.generate_content(prompt)
        analysis = response.text

        # Use regex to split sections for dropdowns
        def extract_section(title, text):
            pattern = rf"## {title}\n(.*?)(\n## |\Z)"
            match = re.search(pattern, text, re.DOTALL)
            return match.group(1).strip() if match else "Not found."

        st.markdown("### 📊 Analysis Result")

        with st.expander("📌 Summary"):
            st.markdown(extract_section("Summary", analysis))

        with st.expander("🔗 Links"):
            st.markdown(extract_section("Links", analysis))

        with st.expander("🗓️ Schedules"):
            st.markdown(extract_section("Schedules", analysis))

        with st.expander("✅ Tasks"):
            st.markdown(extract_section("Tasks", analysis))

# 💬 Chat with Gemini
if chat_text:
    st.markdown("---")
    st.subheader("🤖 Chat with Your WhatsApp Data")

    user_input = st.text_input("Ask a question (e.g., What meetings are planned?)")
    if user_input:
        chat_prompt = f"""
You are an AI assistant. Based on the WhatsApp chat log below, answer this user query clearly:

Query: {user_input}

Chat log:
{chat_text}
"""
        with st.spinner("Thinking..."):
            chat_response = model.generate_content(chat_prompt)
            st.markdown("**Response:**")
            st.markdown(chat_response.text)
