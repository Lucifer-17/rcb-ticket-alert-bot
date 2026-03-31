from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText
import requests
import os

URLS = [
    "https://www.royalchallengers.com/tickets",
    "https://insider.in/",
    "https://www.ticketgenie.in/"
]

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FLAG_FILE = "/tmp/notified.txt"

def send_email(msg_text):
    msg = MIMEText(msg_text)
    msg["Subject"] = "🔥 RCB Tickets LIVE!"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def already_notified():
    return os.path.exists(FLAG_FILE)

def mark_notified():
    with open(FLAG_FILE, "w") as f:
        f.write("sent")

def check_site(page, url):
    page.goto(url, timeout=60000)
    page.wait_for_timeout(5000)

    elements = page.locator("button, a").all()

    for el in elements:
        try:
            text = el.inner_text().lower()
            disabled = el.get_attribute("disabled")

            if ("buy" in text or "ticket" in text or "book" in text):
                if el.is_visible() and disabled is None:
                    return True
        except:
            continue

    return False

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in URLS:
            try:
                if check_site(page, url):
                    if not already_notified():
                        msg = f"🔥 RCB Tickets LIVE!\n{url}"
                        send_email(msg)
                        send_telegram(msg)
                        mark_notified()
                    return
            except:
                continue

        browser.close()
        print("No tickets yet...")

if __name__ == "__main__":
    run()
