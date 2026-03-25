from app.database import Base
from sqlalchemy import Column, Integer, String, JSON

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index = True)
    botname = Column(String(50), nullable = False, unique = True)
    backstory = Column(String(255), nullable=True)

    performance_data = Column(JSON, nullable = False)

    advice_data = Column(JSON, nullable = True)