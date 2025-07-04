from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def start_browser():
    options = Options()
    options.add_argument("--user-data-dir=whatsapp-profile")
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com")
    return driver

def extract_messages(driver, max_chats=5):
    print("Waiting for login...")
    time.sleep(15)  # wait for QR code scan

    chats = driver.find_elements(By.CLASS_NAME, "_3OvU8")[:max_chats]
    all_msgs = []

    for chat in chats:
        try:
            chat.click()
            time.sleep(2)
            messages = driver.find_elements(By.CLASS_NAME, "_21Ahp")
            chat_text = [msg.text for msg in messages if msg.text]
            all_msgs.extend(chat_text)
        except:
            pass
    return "\n".join(all_msgs)
