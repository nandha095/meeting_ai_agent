from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base

class GoogleToken(Base):
    __tablename__ = "google_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    access_token = Column(String(2048), nullable=False)
    refresh_token = Column(String(2048))
    token_uri = Column(String(255))
    scopes = Column(String(1000))
    expiry = Column(DateTime)
