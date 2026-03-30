from app.schemas.user import UserRegister
from app.main import app
from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends
from database import get_db

router = APIRouter()

@router.post("/api/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    authorize = AuthService()
    auth = await authorize.register(db, user_data)
    return auth