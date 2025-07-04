import streamlit as st
from whatsapp_scraper import start_browser, extract_messages
from gemini_utils import analyze_messages
import json

st.set_page_config("WhatsApp Analyzer", layout="wide")

st.title("📱 WhatsApp Message Analyzer using Gemini 2.0 Flash")

if "driver" not in st.session_state:
    st.session_state.driver = None

st.markdown("### Step 1: Connect WhatsApp")

if st.button("🔗 Start WhatsApp Web"):
    st.session_state.driver = start_browser()
    st.success("WhatsApp Web opened. Please scan QR code!")

if st.button("📥 Extract & Analyze Messages"):
    if not st.session_state.driver:
        st.warning("Start WhatsApp Web first!")
    else:
        with st.spinner("Extracting messages..."):
            raw = extract_messages(st.session_state.driver)
            result = analyze_messages(raw)

            st.markdown("## 📊 Analysis Result")
            st.json(json.loads(result))

st.markdown("---")
st.markdown("### 💬 Ask AI about extracted data")
user_input = st.text_input("Enter your query (e.g., What meetings are scheduled?)")

if user_input:
    with st.spinner("Analyzing with Gemini..."):
        full_prompt = f"""Based on this data:
        {raw}

        Answer this question: {user_input}"""
        response = analyze_messages(full_prompt)
        st.markdown("#### 🧠 Gemini Response")
        st.write(response)
