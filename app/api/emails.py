from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ProposalEmailRequest
from app.services.email_service import send_proposal_email
from app.db.deps import get_db
from app.models.proposal import Proposal
from app.models.user import User
from app.models.google_token import GoogleToken
from app.api.auth import get_current_user

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)


@router.post("/send-proposal")
def send_proposal(
    payload: ProposalEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a project proposal email using the logged-in user's Gmail
    """

    subject = "Project Proposal"
    body = """
    <h3>Hello,</h3>
    <p>We would like to propose a project collaboration.</p>
    <p>Please let us know if you'd like to schedule a meeting.</p>
    <br>
    <p>Regards,<br>Nandhakumar</p>
    """

    # 🔐 Ensure Google is connected for this user
    token = db.query(GoogleToken).filter(
        GoogleToken.user_id == current_user.id
    ).first()

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Please connect your Google account before sending proposals"
        )

    # ✅ Send email using THIS user's Gmail
    send_proposal_email(
        db=db,
        user_id=current_user.id,
        to_email=payload.email,
        subject=subject,
        body=body
    )

    # ✅ Save proposal in DB
    proposal = Proposal(
        user_id=current_user.id,
        client_email=payload.email,
        subject=subject,
        body=body,
        status="SENT"
    )

    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return {
        "message": "Proposal sent successfully",
        "proposal_id": proposal.id,
        "sent_from": current_user.email
    }
