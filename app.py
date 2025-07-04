import streamlit as st
import re
from datetime import datetime
from google.generativeai import GenerativeModel, configure

# Configure Gemini
configure(api_key=st.secrets["GEMINI_API_KEY"])
model = GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📲 WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("📁 Upload WhatsApp .txt export", type=["txt"])

# Parse WhatsApp messages with date
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

if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8")
    all_messages = parse_messages(raw_text)

    if not all_messages:
        st.error("No valid messages found.")
    else:
        st.markdown("### 🔎 Filter Options")

        dates = [msg[0] for msg in all_messages]
        min_date = min(dates)
        max_date = max(dates)

        start_date = st.date_input("Start date", value=min_date.date(), min_value=min_date.date(), max_value=max_date.date())
        end_date = st.date_input("End date", value=max_date.date(), min_value=min_date.date(), max_value=max_date.date())

        sort_order = st.radio("Sort by", ["Newest First", "Oldest First"])

        filtered = [msg for msg in all_messages if start_date <= msg[0].date() <= end_date]
        filtered.sort(reverse=(sort_order == "Newest First"))

        chat_text = "\n".join([msg[1] for msg in filtered])

        st.markdown(f"### 💬 Filtered messages: {len(filtered)}")

        if st.button("📊 Analyze Messages"):
            prompt = f"""
Analyze the WhatsApp messages below.

Extract:
- 🔔 Reminders
- 🗓️ Meeting schedules or time-based events
- 🔗 Shared links
- ✅ To-do items or important actions

Format clearly with headings and timestamps.

Chat:
{chat_text}
"""
            with st.spinner("Analyzing..."):
                response = model.generate_content(prompt)
                st.subheader("📌 Gemini Summary")
                st.markdown(response.text)

        st.divider()
        st.subheader("🤖 Ask the Assistant")
        user_q = st.text_input("Ask a question (e.g. 'What reminders are there?')")

        if user_q:
            q_prompt = f"""
User question: {user_q}

Based only on this WhatsApp chat:
{chat_text}
"""
            with st.spinner("Answering..."):
                answer = model.generate_content(q_prompt)
                st.markdown("**Answer:**")
                st.markdown(answer.text)
