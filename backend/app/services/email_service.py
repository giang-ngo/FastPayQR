from email.message import EmailMessage
import smtplib
from backend.app.config import mail_settings


def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str = None):
    msg = EmailMessage()
    msg["From"] = mail_settings.MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="invoice.pdf")

    with smtplib.SMTP(mail_settings.SMTP_HOST, mail_settings.SMTP_PORT) as server:
        if mail_settings.SMTP_USE_TLS:
            server.starttls()
        server.login(mail_settings.SMTP_USERNAME, mail_settings.SMTP_PASSWORD)
        server.send_message(msg)