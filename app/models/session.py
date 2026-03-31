from app.database import Base
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func

class SessionTable(Base):
    __tablename__ = "sessions"

    player_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String, primary_key=True, index=True)
    session_data = Column(JSON, nullable = False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)