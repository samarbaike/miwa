from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

# 1. THE ABSTRACT PARENT CLASS
class BaseUser(Base):
    __abstract__ = True 

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 2. THE PLAYER CHILD CLASS
class Player(BaseUser):
    __tablename__ = "players"
    
    password_hash = Column(String(255), nullable=False)
    rank = Column(Integer, default=110) 
    wins = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    total_matches = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)

# 3. THE ADMIN CHILD CLASS
class Admin(BaseUser):
    __tablename__ = "admins"

    password_hash = Column(String(255), nullable=False)