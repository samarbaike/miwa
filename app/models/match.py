import enum
from app.database import Base
from sqlalchemy import Column, Integer, String, JSON, Enum

class MatchStatus(enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class MatchMode(enum.Enum):
    RANKED = "ranked"
    PRACTICE = "practice"
    INVITE = "invite"

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key = True, index = True)

    #player tracking
    player1_id = Column(Integer, nullable = False)
    player2_id = Column(Integer, nullable = True) # Nullable untill someone joins
    player2_bot_id = Column(Integer, nullable = True)

    #Enums
    status = Column(Enum(MatchStatus), default = MatchStatus.WAITING, nullable = False)
    mode = Column(Enum(MatchMode), nullable = False)

    winner_id = Column(Integer, nullable = True)
    player1_score = Column(Integer, default = 0)
    player2_score = Column(Integer, default = 0)

    #questions
    questions_data = Column(JSON, nullable = True)
    answers_data = Column(JSON, nullable = True)

    invite_code = Column(String(6), nullable = True)
