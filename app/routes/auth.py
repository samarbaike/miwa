from app.schemas.user import UserRegister, LoginRequest, UserResponse
from app.services.auth_service import AuthService
from app.database import get_db
from app.models.user import Player
from app.models.session import SessionTable
from app.core.dependencies import get_current_player

from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session


router = APIRouter()

@router.post("/api/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    authorize = AuthService()
    auth = authorize.register(db, user_data)
    return auth

@router.post("/api/login", response_model=UserResponse)
def login(user_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService()
    session, token, player = auth_service.login(db, user_data)
    response.set_cookie(key="session_id", 
                        value=token, 
                        httponly=True, 
                        max_age= 24*60*60, 
                        samesite="lax",
                        #secure=True <= enable in production(when https address is acquired) 
    )

    return player

@router.get("/api/user/me", response_model = UserResponse)
def testing(current_player: Player = Depends(get_current_player)):
    return current_player

@router.post("/api/logout")
def logout(response: Response, 
           session_id: str = Cookie(None),
           db: Session = Depends(get_db)):
    deleted = db.query(SessionTable).filter(SessionTable.session_token == session_id).delete()    
    db.commit()

    response.delete_cookie("session_id")

    if deleted == 0:
        return {"message":"User is already logged out"}
    return {"message":"Logout successful"}
    
