from app.schemas.user import UserRegister
from app.main import app
from app.services.auth_service import AuthService
from fastapi import APIRouter

router = APIRouter()
authorize = AuthService()

@router.post("/api/register")
async def register(user_data: UserRegister):
    auth = authorize.register(user_data)
    return auth
