from app.database import get_db
from app.models.session import SessionTable
from app.models.user import Player

from sqlalchemy.orm import Session
from fastapi import Cookie, HTTPException, Depends
from datetime import datetime
import pytz

def get_current_player(session_id: str = Cookie(None), db: Session = Depends(get_db)):

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 2. Look up the session in the database
    session = db.query(SessionTable).filter(SessionTable.session_token == session_id).first()
    
    # 3. Does the session exist? Is it expired?
    if session is None or session.expires_at < datetime.now(pytz.utc):
        raise HTTPException(status_code=401, detail="No session found")
    
    # 4. Find the actual user
    player = db.query(Player).filter(Player.id == session.player_id).first()

    # 5. Return the user object!
    # return user
    if player is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return player