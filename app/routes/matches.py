from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.match_services import MatchService
from app.core.dependencies import get_current_player
from app.models.player import Player


router = APIRouter()

@router.post("/api/matches/create-invite")
def create_invited_match(db: Session=Depends(get_db), current_player: Player=Depends(get_current_player) ):
    room_code = MatchService.create_invite_match(db, current_player.id)
    return {"room code":room_code}