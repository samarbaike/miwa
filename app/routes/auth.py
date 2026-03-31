from app.schemas.user import UserRegister, LoginRequest, UserResponse
from app.services.auth_service import AuthService
from app.database import get_db
from app.models.user import Player
from app.core.dependencies import get_current_player

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session


router = APIRouter()

@router.post("/api/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    authorize = AuthService()
    auth = authorize.register(db, user_data)
    return auth

@router.post("/api/login")
def login(user_data: LoginRequest,response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService()
    session, token = auth_service.login(db, user_data)
    response.set_cookie(key="session_id", value=token, httponly=True)
    return {"message": "Login successful"}

@router.get("/api/user/me", response_model = UserResponse)
def testing(current_player: Player = Depends(get_current_player)):
    return current_player