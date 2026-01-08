from app.db.session import SessionLocal
from app.services.reply_processor import process_replies
from app.models.user import User


def run_reply_worker():
    db = SessionLocal()
    try:
        users = db.query(User).all()

        if not users:
            print("⚠️ No users found. Skipping reply processing.")
            return

        for user in users:
            print(f"👤 Processing replies for user: {user.email}")
            try:
                process_replies(db, user_id=user.id)
            except Exception as e:
                print(
                    f"❌ Error processing replies for user {user.email}: {e}"
                )

    finally:
        db.close()
