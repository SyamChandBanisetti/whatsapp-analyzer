import streamlit as st
import re
from datetime import datetime
from google.generativeai import GenerativeModel, configure

# 🔐 Set up Gemini API
configure(api_key=st.secrets["GEMINI_API_KEY"])
model = GenerativeModel("gemini-2.0-flash")

# 🧭 Page Config
st.set_page_config(page_title="📲 WhatsApp Chat Analyzer", layout="wide")
st.title("📲 WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("📁 Upload your WhatsApp Chat (.txt file)", type=["txt"])

# 🔍 Parse messages with timestamps
def parse_messages(text):
    pattern = r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s+(\d{1,2}:\d{2})\s*(AM|PM)?\s+-"
    messages = []
    for line in text.splitlines():
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
    return messages

# 🧾 If chat file is uploaded
if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8")
    all_messages = parse_messages(raw_text)

    if not all_messages:
        st.error("❌ No valid messages detected. Please check your file.")
    else:
        st.markdown("## 🔎 Filter & Sort Options")

        dates = [msg[0] for msg in all_messages]
        min_date = min(dates)
        max_date = max(dates)

        col1, col2, col3 = st.columns([1.3, 1.3, 1])

        with col1:
            start_date = st.date_input("📅 Start Date", value=min_date.date(), min_value=min_date.date(), max_value=max_date.date())

        with col2:
            end_date = st.date_input("📅 End Date", value=max_date.date(), min_value=min_date.date(), max_value=max_date.date())

        with col3:
            sort_order = st.selectbox("🔃 Sort Order", ["Newest First", "Oldest First"])

        filtered = [msg for msg in all_messages if start_date <= msg[0].date() <= end_date]
        filtered.sort(reverse=(sort_order == "Newest First"))

        chat_text = "\n".join([msg[1] for msg in filtered])

        st.markdown(f"### 💬 Messages Selected: `{len(filtered)}`")
        st.caption(f"From {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')} | Order: {sort_order}")

        if st.toggle("📝 Show Filtered Raw Messages"):
            st.code(chat_text, language="text")

        # 📊 Summarize with Gemini
        if st.button("📊 Summarize with Gemini"):
            prompt = f"""
From the WhatsApp messages below, extract and summarize:

- 🔔 Reminders
- 🗓️ Meeting schedules
- 🔗 Shared links
- ✅ Action items or follow-ups

Include dates and times wherever relevant.
Present the summary in clean Markdown with bullet points and headings.

Chat:
{chat_text}
"""
            with st.spinner("Summarizing with Gemini..."):
                response = model.generate_content(prompt)
                st.subheader("📌 Summary")
                st.markdown(response.text)

        # 🤖 Chatbot
        st.markdown("---")
        st.subheader("🤖 Chat with Your Chat Logs")
        user_q = st.text_input("Ask a question (e.g. 'What were the meeting links shared?')")

        if user_q:
            q_prompt = f"""
You're an assistant analyzing WhatsApp chat history. Based on the following chat and user query, provide a clear and concise answer.

User question:
{user_q}

Chat:
{chat_text}
"""
            with st.spinner("Thinking..."):
                reply = model.generate_content(q_prompt)
                st.markdown("**Answer:**")
                st.markdown(reply.text)
