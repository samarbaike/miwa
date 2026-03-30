from app.schemas.user import UserRegister
from app.main import app
from app.services.auth_service import AuthService
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/register")
async def register(user_data: UserRegister):
    authorize = AuthService()
    auth = authorize.register(user_data)
    return auth