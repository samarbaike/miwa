from app.models.user import Player
from app.models.session import SessionTable
from app.schemas.user import UserRegister, LoginRequest
from app.core.security import Hasher

from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4
from datetime import datetime, timedelta
import pytz


class AuthService:
    def register(self, session: Session, user_in: UserRegister):
        existing_user = session.query(Player).filter(Player.email == user_in.email).first()

        if existing_user is None:
            hashed_pw = Hasher.get_password_hash(user_in.password)

            new_player = Player(username = user_in.username, email = user_in.email, password_hash = hashed_pw)

            session.add(new_player)
            session.commit()
            session.refresh(new_player)
            return new_player
        
        else:
            raise HTTPException(status_code=400, detail=f"The User with email {user_in.email} exists!")
        

    def login(self, session: Session, user_in: LoginRequest):
        existing_user = session.query(Player).filter(Player.username == user_in.username).first()
        if existing_user is None:
            raise HTTPException(status_code=401, detail="User with such username doesn't exist")
        else:
            if Hasher.verify_password(user_in.password, existing_user.password_hash):
                new_session_token = str(uuid4())
                created_at = datetime.now(pytz.utc)
                expires_at = created_at + timedelta(days=1)
                new_session = SessionTable(player_id=existing_user.id, 
                                            session_token=new_session_token,
                                            session_data={},
                                            expires_at=expires_at)
                session.add(new_session)
                session.commit()
                session.refresh(new_session)

                return new_session, new_session_token
        
            else:
                raise HTTPException(status_code=401, detail="Wrong password")
    