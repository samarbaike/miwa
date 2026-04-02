from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.match_services import MatchService
from app.core.dependencies import get_current_player
from app.models.player import Player
from app.models.match import Match


router = APIRouter()

@router.post("/api/matches/create-invite")
def create_invited_match(db: Session=Depends(get_db), current_player: Player=Depends(get_current_player) ):
    room_code = MatchService.create_invite_match(db, current_player.id)
    return {"room_code":room_code}


@router.get("/api/match/{id}")
def get_match_status(id: int, db: Session=Depends(get_db)):
    match = db.query(Match).filter(Match.id == id).first()
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match not found")
    return match