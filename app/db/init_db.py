from app.db.session import engine
from app.db.base import Base

# Import all models so Base knows them
from app.models.user import User
from app.models.google_token import GoogleToken
from app.models.proposal import Proposal
from app.models.reply import Reply
from app.models.meeting import Meeting

def init_db():
    Base.metadata.create_all(bind=engine)
