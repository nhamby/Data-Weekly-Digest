import os
import pandas as pd
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from datetime import datetime

load_dotenv()
GMAIL_EMAIL_ADDRESS = os.getenv("GMAIL_EMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def create_email_body(df: pd.DataFrame) -> str:

    html_content = "<html><body>"
    html_content += "<h1> Morning ARCHie Data Procurement News Briefing</h1>"
    html_content += "<p>Here's a summary of articles from the past week:</p>"

    for index, row in df.iterrows():
        html_content += "<div style='margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 8px;'>"
        html_content += f"<h2><a href='{row['url']}' style='color: #0056b3; text-decoration: none;'>{row['title']}</a></h2>"
        html_content += f"<p><strong>Source:</strong> {row['source']}</p>"
        html_content += f"<p>{row['summary']}</p>"
        html_content += "</div>"

    html_content += "</body></html>"
    return html_content


def send_news_email(df: pd.DataFrame, recipient_email: str):
    sender_email = GMAIL_EMAIL_ADDRESS
    sender_password = GMAIL_APP_PASSWORD
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    email_subject = f"Your Monday News Briefing - {datetime.now().strftime('%Y-%m-%d')}"
    email_body_html = create_email_body(df)

    msg = MIMEText(email_body_html, "html")
    msg["Subject"] = email_subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent successfully to {recipient_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")
