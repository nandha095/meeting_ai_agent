import base64
import email
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.services.google_credentials import get_google_credentials


def get_gmail_service(db: Session, user_id: int):
    """
    Returns Gmail service for a specific user
    """
    creds = get_google_credentials(db, user_id)
    return build("gmail", "v1", credentials=creds)


def fetch_recent_emails(db: Session, user_id: int):
    """
    Fetch recent inbox emails for a specific user
    """
    service = get_gmail_service(db, user_id)

    # Only inbox, not sent by user, not system mails
    results = service.users().messages().list(
        userId="me",
        q="is:inbox -from:me -from:mailer-daemon -from:postmaster"
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="raw"
        ).execute()

        raw = base64.urlsafe_b64decode(msg_data["raw"])
        email_msg = email.message_from_bytes(raw)

        body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = email_msg.get_payload(decode=True).decode(errors="ignore")

        emails.append({
            "message_id": msg["id"],
            "from": email_msg.get("From"),
            "subject": email_msg.get("Subject"),
            "body": body
        })

    return emails
