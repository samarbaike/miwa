from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserStats, UserUpdate
from app.database import get_db
from app.core.dependencies import get_current_player
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

@router.put("/api/user/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_data: UserUpdate, # Make sure to import or define this Pydantic schema
    db: Session = Depends(get_db), 
    current_user: Player = Depends(get_current_player)
):
    # 1. Authorization: Ensure the user is updating their own account
    if current_user.id != user_id:
        raise HTTPException(status_code=404, detail="Not authorized to update this account")

    # 2. Query the user
    user = db.query(Player).filter(Player.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 3. Update logic (applies only provided fields)
    update_dict = user_data.model_dump(exclude_unset=True) # use .dict() if using Pydantic v1
    for key, value in update_dict.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/api/user/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: Player = Depends(get_current_player)
):
    # 1. Authorization: Ensure the user is deleting their own account
    if current_user.id != user_id:
        raise HTTPException(status_code=404, detail="Not authorized to delete this account")

    # 2. Query the user properly via SQLAlchemy
    user = db.query(Player).filter(Player.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 3. Delete properly via SQLAlchemy
    db.delete(user)
    db.commit()
    
    return {"message": "Oyunchu ochuruldu"}

    
