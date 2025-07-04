import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_messages(raw_text):
    prompt = f"""You are a message summarizer. Extract:
    1. Important messages
    2. Meeting links or any URLs
    3. Schedules or date/time-related events

    Output in JSON with keys: important_messages, links, schedules.
    Messages:
    {raw_text}
    """
    res = model.generate_content(prompt)
    return res.text
