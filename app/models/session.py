from app.database import Base
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
class SessionTable(Base):
    __tablename__ = "session"

    sid = Column(String, primary_key=True, index=True)
    sess = Column(JSON, nullable = False)
    expire = Column(DateTime(timezone=True))