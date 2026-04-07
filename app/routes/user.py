from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserStats
from app.database import get_db
from app.models.user import Player


router = APIRouter()

@router.get("/api/user/{user_id}", response_model=UserResponse)
def get_user_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Player).filter(Player.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} doesn't exist")
    return user

@router.get("/api/user/{user_id}/stats", response_model=UserStats)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Player).filter(Player.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} doesn't exist")
    return user

@router.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    top_20 = db.query(Player).order_by(Player.elo.desc()).limit(20).all()
    return top_20
    
