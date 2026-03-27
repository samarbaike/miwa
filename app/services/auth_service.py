from app.models.user import Player
from app.schemas.user import UserRegister
from app.core.security import Hasher
from sqlalchemy.orm import Session
from fastapi import HTTPException
class AuthService:
    async def register(self, session: Session, user_in: UserRegister):
        existing_user = session.query(Player).filter(Player.email == user_in.email).first()

        if existing_user == None:
            hashed_pw = Hasher.get_password_hash(user_in.password)

            new_player = Player(username = user_in.username, email = user_in.email, password_hash = hashed_pw)

            session.add(new_player)
            session.commit()
            session.refresh(new_player)
            return new_player
        
        else:
            raise HTTPException(status_code=400, detail=f"The User with email {user_in.email} exists!")
