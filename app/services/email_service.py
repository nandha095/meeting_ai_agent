# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.core.config import settings


# def send_proposal_email(to_email: str, subject: str, body: str):
#     msg = MIMEMultipart()
#     msg["From"] = settings.EMAIL_HOST_USER
#     msg["To"] = to_email
#     msg["Subject"] = subject

#     msg.attach(MIMEText(body, "html"))

#     server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
#     server.starttls()
#     server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#     server.send_message(msg)
#     server.quit()

# def send_email(to_email: str, subject: str, body: str):
#     """
#     Generic email sender used by all services
#     """
#     from email.mime.text import MIMEText
#     import smtplib
#     from app.core.config import settings

#     msg = MIMEText(body, "html")
#     msg["Subject"] = subject
#     msg["From"] = settings.EMAIL_HOST_USER
#     msg["To"] = to_email

#     with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
#         server.starttls()
#         server.login(
#             settings.EMAIL_HOST_USER,
#             settings.EMAIL_HOST_PASSWORD
#         )
#         server.send_message(msg)

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session

from app.services.gmail_reader import get_gmail_service


# -------------------------------------------------
# PROPOSAL EMAIL (GOOGLE GMAIL API – MULTI USER)
# -------------------------------------------------
def send_proposal_email(
    db: Session,
    user_id: int,
    to_email: str,
    subject: str,
    body: str
):
    """
    Sends proposal email using the logged-in user's Gmail account
    """

    service = get_gmail_service(db, user_id)

    msg = MIMEMultipart("alternative")
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    raw_message = base64.urlsafe_b64encode(
        msg.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()


# -------------------------------------------------
# GENERIC EMAIL (OPTIONAL – SYSTEM EMAILS ONLY)
# -------------------------------------------------
# ⚠️ Use this ONLY for system notifications
# ⚠️ NOT for user Gmail sending
def send_system_email(
    smtp_user: str,
    smtp_password: str,
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str | None = None
):
    import smtplib

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body_text, "plain"))

    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
