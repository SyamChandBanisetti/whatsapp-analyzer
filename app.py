import streamlit as st
import os
import re
from datetime import datetime, timedelta
from google.generativeai import GenerativeModel, configure

# Gemini API setup
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📲 WhatsApp Chat Analyzer")

st.markdown("### Step 1: Upload WhatsApp Chat Export (.txt)")
uploaded_file = st.file_uploader("📁 Upload WhatsApp Chat File", type=["txt"])

def extract_recent_messages(text, days=7):
    """
    Filters messages from the past `days` number of days and returns them sorted from latest to oldest.
    """
    lines = text.splitlines()
    recent_lines = []
    now = datetime.now()
    
    # WhatsApp date pattern: "06/30/2024, 9:01 AM -"
    date_pattern = r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s+-"

    for line in lines:
        match = re.match(date_pattern, line)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            try:
                # Try MM/DD/YYYY
                msg_datetime = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M %p")
            except:
                try:
                    # Try DD/MM/YYYY
                    msg_datetime = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M %p")
                except:
                    continue
            if msg_datetime >= now - timedelta(days=days):
                recent_lines.append((msg_datetime, line))

    # Sort by most recent
    recent_lines.sort(reverse=True)
    return [line for dt, line in recent_lines]

# Main Analysis
if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8")
    recent_chat_lines = extract_recent_messages(raw_text, days=7)
    
    if not recent_chat_lines:
        st.warning("No recent messages found in the last 7 days.")
    else:
        filtered_chat = "\n".join(recent_chat_lines)

        if st.button("📊 Analyze Reminders & Meetings"):
            prompt = f"""
From the following WhatsApp chat log (last 7 days), extract:
1. 🔔 Reminders (look for 'reminder', 'don't forget', etc.)
2. 🕒 Meeting schedules (zoom calls, calls, timings, calendar items)
3. 🔗 Important links
4. ✅ Action items

Sort the results by most recent date (descending). Show in markdown with date and time stamps.

Chat log:
{filtered_chat}
"""
            with st.spinner("Analyzing recent chat messages..."):
                response = model.generate_content(prompt)
                st.subheader("📌 Gemini Analysis")
                st.markdown(response.text)

        st.markdown("---")
        st.subheader("🤖 Chatbot: Ask About Recent Messages")
        user_question = st.text_input("Ask a question (e.g., What Zoom meetings are scheduled?)")

        if user_question:
            chat_prompt = f"""
You are an AI assistant analyzing a WhatsApp chat log from the last 7 days.
Answer the user's question accurately using only the information below.

User's question:
{user_question}

Chat log:
{filtered_chat}
"""
            with st.spinner("Thinking..."):
                chat_response = model.generate_content(chat_prompt)
                st.markdown("**Answer:**")
                st.markdown(chat_response.text)
