# from datetime import datetime, timedelta
# import pytz
# import re

# from app.services.gmail_reader import fetch_recent_emails
# from app.services.ai_intent import detect_meeting_intent
# from app.services.time_extractor import extract_time_and_timezone
# from app.services.meeting_service import create_google_meet
# from app.services.meeting_email_service import (
#     send_meeting_link_email,
#     send_schedule_choice_email,
#     send_not_interested_email,
# )
# from app.services.email_cleaner import clean_email_body
# from app.services.llm_extractor import llm_extract_intent_and_time

# from app.models.reply import Reply
# from app.models.meeting import Meeting
# from app.models.proposal import Proposal
# from app.models.google_token import GoogleToken

# IST_TZ = pytz.timezone("Asia/Kolkata")


# def extract_email_address(sender: str) -> str:
#     if not sender:
#         return ""
#     match = re.search(r"<(.+?)>", sender)
#     return match.group(1) if match else sender


# def process_replies(db, user_id: int):
#     # 0️⃣ Ensure Google connected
#     token = db.query(GoogleToken).filter(
#         GoogleToken.user_id == user_id
#     ).first()

#     if not token:
#         print(f"⚠️ User {user_id} has no Google token. Skipping.")
#         return

#     emails = fetch_recent_emails(db, user_id)

#     for email in emails:
#         print("\n🔎 Gmail message_id:", email["message_id"])

#         # 1️⃣ Deduplication
#         if db.query(Reply).filter(
#             Reply.gmail_message_id == email["message_id"],
#             Reply.user_id == user_id
#         ).first():
#             print("⏭️ Already processed")
#             continue

#         sender_email = extract_email_address(email.get("from"))

#         # 2️⃣ Block system senders
#         if any(bad in (email.get("from") or "").lower() for bad in [
#             "noreply", "mailer-daemon", "postmaster", "newsletter", "linkedin"
#         ]):
#             continue

#         # 3️⃣ Clean body
#         body = clean_email_body(email.get("body", ""))
#         if not body:
#             continue

#         # 4️⃣ Rule-based intent
#         intent = detect_meeting_intent(body)
#         print("🧠 RULE INTENT:", intent)

#         # 5️⃣ LLM fallback (safe)
#         llm_result = None
#         if intent["confidence"] < 0.75:
#             try:
#                 llm_result = llm_extract_intent_and_time(body)
#             except Exception as e:
#                 print("❌ LLM failed:", e)

#         # 6️⃣ Map LLM → system intents
#         if llm_result:
#             print("🤖 LLM RAW:", llm_result)

#             if llm_result["intent"] == "no_interest":
#                 intent = {"intent": "NO_INTEREST", "confidence": 0.95}

#             elif llm_result["intent"] == "schedule_now":
#                 intent = {"intent": "ASKED_TO_SCHEDULE", "confidence": 0.95}

#             elif llm_result["intent"] == "schedule_later":
#                 intent = {"intent": "INTERESTED_NO_TIME", "confidence": 0.9}

#         print("✅ FINAL INTENT:", intent)

#         # 7️⃣ Find proposal
#         proposal = db.query(Proposal).filter(
#             Proposal.client_email == sender_email,
#             Proposal.user_id == user_id
#         ).order_by(Proposal.created_at.desc()).first()

#         if not proposal:
#             continue

#         # 8️⃣ Save reply
#         reply = Reply(
#             user_id=user_id,
#             proposal_id=proposal.id,
#             gmail_message_id=email["message_id"],
#             sender=email.get("from"),
#             subject=email.get("subject"),
#             body=body,
#             meeting_interest=intent["intent"] != "NO_INTEREST",
#             confidence=intent["confidence"],
#         )

#         db.add(reply)
#         db.commit()
#         db.refresh(reply)

#         # 9️⃣ No interest
#         if intent["intent"] == "NO_INTEREST":
#             proposal.status = "REJECTED"
#             db.commit()
#             send_not_interested_email(db, user_id, sender_email)
#             continue

#         # 🔟 Interested but no time
#         if intent["intent"] == "INTERESTED_NO_TIME":
#             proposal.status = "WAITING_FOR_TIME"
#             db.commit()
#             send_schedule_choice_email(db, user_id, sender_email)
#             continue

#         # 1️⃣1️⃣ Determine meeting time
#         if intent["intent"] == "ASKED_TO_SCHEDULE":
#             start_time = datetime.now(IST_TZ) + timedelta(minutes=30)
#             client_time = None
#             client_timezone = None

#         else:
#             extracted = extract_time_and_timezone(body)
#             if not extracted:
#                 send_schedule_choice_email(db, user_id, sender_email)
#                 continue

#             start_time = extracted["ist_datetime"]
#             client_time = extracted["client_datetime"]
#             client_timezone = extracted["client_timezone"]

#         # 1️⃣2️⃣ Prevent duplicate meetings
#         if db.query(Meeting).filter(
#             Meeting.reply_id == reply.id,
#             Meeting.user_id == user_id
#         ).first():
#             continue

#         # 1️⃣3️⃣ Create Google Meet
#         meeting_data = create_google_meet(
#             db=db,
#             user_id=user_id,
#             summary="Project Proposal – Discussion",
#             description="Meeting scheduled based on client response",
#             start_time=start_time,
#             duration_minutes=30,
#         )

#         meeting = Meeting(
#             user_id=user_id,
#             proposal_id=proposal.id,
#             reply_id=reply.id,
#             meet_link=meeting_data["meet_link"],
#             start_time=meeting_data["start_time"],
#             end_time=meeting_data["end_time"],
#         )

#         db.add(meeting)
#         proposal.status = "MEETING_SCHEDULED"
#         db.commit()

#         # 1️⃣4️⃣ Send meeting email
#         send_meeting_link_email(
#             db=db,
#             user_id=user_id,
#             to_email=sender_email,
#             meet_link=meeting.meet_link,
#             client_time=client_time,
#             ist_time=start_time,
#             client_timezone=client_timezone,
#         )

#         print("✅ Meeting scheduled & email sent")

from datetime import datetime, timedelta
import pytz
import re

from app.services.gmail_reader import fetch_recent_emails
from app.services.ai_intent import detect_meeting_intent
from app.services.time_extractor import extract_time_and_timezone
from app.services.llm_extractor import llm_extract_intent_and_time
from app.services.meeting_service import create_google_meet
from app.services.meeting_email_service import (
    send_meeting_link_email,
    send_schedule_choice_email,
    send_not_interested_email,
)
from app.services.email_cleaner import clean_email_body
from app.services.timezone_utils import (
    convert_client_time_to_ist,
    convert_calendar_relative_to_ist,
)

from app.models.reply import Reply
from app.models.meeting import Meeting
from app.models.proposal import Proposal
from app.models.google_token import GoogleToken

IST_TZ = pytz.timezone("Asia/Kolkata")

AMBIGUOUS_WORDS = [
    "next", "tomorrow", "today",
    "evening", "morning", "afternoon",
    "later", "soon"
]


def extract_email_address(sender: str) -> str:
    if not sender:
        return ""
    match = re.search(r"<(.+?)>", sender)
    return match.group(1) if match else sender


def process_replies(db, user_id: int):

    # -------------------------------------------------
    # 0️⃣ GOOGLE TOKEN CHECK
    # -------------------------------------------------
    token = db.query(GoogleToken).filter(
        GoogleToken.user_id == user_id
    ).first()

    if not token:
        print(f"⚠️ User {user_id} has no Google token. Skipping.")
        return

    emails = fetch_recent_emails(db, user_id)

    for email in emails:
        try:
            print("\n🔎 Gmail message_id:", email["message_id"])

            # -------------------------------------------------
            # 1️⃣ DEDUPLICATION (HARD STOP)
            # -------------------------------------------------
            if db.query(Reply).filter(
                Reply.gmail_message_id == email["message_id"],
                Reply.user_id == user_id
            ).first():
                print("⏭️ Already processed. Skipping.")
                continue

            sender_email = extract_email_address(email.get("from"))
            subject = (email.get("subject") or "").lower()

            if not any(k in subject for k in ["proposal", "meeting", "schedule"]):
                continue

            body = clean_email_body(email.get("body", ""))
            if not body:
                continue

            # -------------------------------------------------
            # 2️⃣ RULE INTENT
            # -------------------------------------------------
            rule_intent = detect_meeting_intent(body)
            print("🧠 RULE INTENT:", rule_intent)

            # -------------------------------------------------
            # 3️⃣ LLM (ONLY IF AMBIGUOUS)
            # -------------------------------------------------
            llm_result = None
            if any(w in body.lower() for w in AMBIGUOUS_WORDS):
                print("⚠️ Ambiguous time → calling LLM")
                llm_result = llm_extract_intent_and_time(body)
                print("🤖 LLM RESULT:", llm_result)

            # -------------------------------------------------
            # 4️⃣ FINAL INTENT
            # -------------------------------------------------
            final_intent = rule_intent

            if llm_result and llm_result.get("intent") == "CLIENT_PROVIDED_TIME":
                final_intent = {
                    "intent": "CLIENT_PROVIDED_TIME",
                    "confidence": 0.95,
                    "source": "LLM",
                    "calendar_relative": llm_result.get("calendar_relative"),
                    "relative_day": llm_result.get("relative_day"),
                    "relative_modifier": llm_result.get("relative_modifier"),
                    "time": llm_result.get("time"),
                    "timezone": llm_result.get("timezone"),
                }

            print("✅ FINAL INTENT:", final_intent)

            # -------------------------------------------------
            # 5️⃣ FIND PROPOSAL
            # -------------------------------------------------
            proposal = db.query(Proposal).filter(
                Proposal.client_email == sender_email,
                Proposal.user_id == user_id
            ).order_by(Proposal.created_at.desc()).first()

            if not proposal:
                print("⚠️ No matching proposal")
                continue

            # -------------------------------------------------
            # 6️⃣ SAVE REPLY
            # -------------------------------------------------
            reply = Reply(
                user_id=user_id,
                proposal_id=proposal.id,
                gmail_message_id=email["message_id"],
                sender=email.get("from"),
                subject=email.get("subject"),
                body=body,
                meeting_interest=final_intent["intent"] != "NO_INTEREST",
                confidence=final_intent["confidence"],
            )

            db.add(reply)
            db.commit()
            db.refresh(reply)

            # -------------------------------------------------
            # 7️⃣ NO INTEREST
            # -------------------------------------------------
            if final_intent["intent"] == "NO_INTEREST":
                proposal.status = "REJECTED"
                db.commit()
                send_not_interested_email(db, user_id, sender_email)
                continue

            # -------------------------------------------------
            # 8️⃣ INTERESTED BUT NO TIME
            # -------------------------------------------------
            if final_intent["intent"] == "INTERESTED_NO_TIME":
                proposal.status = "WAITING_FOR_TIME"
                db.commit()
                send_schedule_choice_email(db, user_id, sender_email)
                continue

            # -------------------------------------------------
            # 9️⃣ RESOLVE MEETING TIME
            # -------------------------------------------------
            if final_intent["intent"] == "ASKED_TO_SCHEDULE":
                start_time = datetime.now(IST_TZ) + timedelta(minutes=30)
                client_time = None
                client_timezone = None

            elif final_intent["intent"] == "CLIENT_PROVIDED_TIME":

                # 🔥 CASE 1: today / tomorrow
                if final_intent.get("calendar_relative"):
                    print("🤖 USING LLM CALENDAR RELATIVE")

                    client_dt, ist_dt = convert_calendar_relative_to_ist(
                        time_str=final_intent["time"],
                        timezone=final_intent["timezone"],
                        calendar_relative=final_intent["calendar_relative"],
                    )

                # 🔥 CASE 2: next friday
                elif final_intent.get("relative_day"):
                    print("🤖 USING LLM WEEKDAY RELATIVE")

                    client_dt, ist_dt = convert_client_time_to_ist(
                        time_str=final_intent["time"],
                        timezone=final_intent["timezone"],
                        weekday=final_intent["relative_day"],
                        modifier=final_intent.get("relative_modifier"),
                    )

                # 🔥 CASE 3: exact time (rule-based)
                else:
                    extracted = extract_time_and_timezone(body)
                    if not extracted:
                        send_schedule_choice_email(db, user_id, sender_email)
                        continue

                    client_dt = extracted["client_datetime"]
                    ist_dt = extracted["ist_datetime"]

                start_time = ist_dt
                client_time = client_dt
                client_timezone = final_intent["timezone"]

            else:
                continue

            # -------------------------------------------------
            # 🔟 PREVENT DUPLICATE MEETINGS
            # -------------------------------------------------
            if db.query(Meeting).filter(
                Meeting.reply_id == reply.id,
                Meeting.user_id == user_id
            ).first():
                print("⏭️ Meeting already exists. Skipping.")
                continue

            # -------------------------------------------------
            # 1️⃣1️⃣ CREATE GOOGLE MEET
            # -------------------------------------------------
            meeting_data = create_google_meet(
                db=db,
                user_id=user_id,
                summary="Project Proposal – Discussion",
                description="Meeting scheduled based on client response",
                start_time=start_time,
                duration_minutes=30,
            )

            meeting = Meeting(
                user_id=user_id,
                proposal_id=proposal.id,
                reply_id=reply.id,
                meet_link=meeting_data["meet_link"],
                start_time=meeting_data["start_time"],
                end_time=meeting_data["end_time"],
            )

            db.add(meeting)
            proposal.status = "MEETING_SCHEDULED"
            db.commit()

            # -------------------------------------------------
            # 1️⃣2️⃣ SEND EMAIL
            # -------------------------------------------------
            send_meeting_link_email(
                db=db,
                user_id=user_id,
                to_email=sender_email,
                meet_link=meeting.meet_link,
                client_time=client_time,
                ist_time=start_time,
                client_timezone=client_timezone,
            )

            print("✅ Meeting scheduled & email sent")

        except Exception as e:
            db.rollback()
            print(f"❌ Error processing reply: {e}")
