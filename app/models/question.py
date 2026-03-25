from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, JSON, ARRAY
from sqlalchemy.sql import func

class Question(Base):
    __abstract__=True

    id = Column(Integer, primary_key = True, index = True)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

class MultipleChoice(Question):
    __tablename__ = "multiple_choice"

    body = Column(String(255),nullable = False)
    options = Column(JSON, nullable = False)
    correct_answer = Column(Integer)
    category = Column(String(100), nullable = False)
    image = Column(String, nullable = True)

"""class ColumnBased(Question):
    __tablename__ = "column_based"

    body = Column(String(255), nullabel = False)
    options = Column(ARRAY, nullable = False)
    correct_answer = Column(Integer)
    category = Column(String(100), nullable = False)
    image = Column(String, nullable = True)"""