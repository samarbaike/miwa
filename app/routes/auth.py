from app.schemas.user import UserRegister
from app.main import app
from app.services.auth_service import AuthService

authorize = AuthService()

@app.post("/api/register")
async def register():
    return authorize
