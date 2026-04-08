from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.match_service import MatchService
from app.core.dependencies import get_current_player
from app.models.user import Player
from app.models.match import Match
from app.services.matchmaking_service import miwa_pool, WaitingPlayer

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

@router.post("/api/matchmaking/join")
def matchmaking(category: str, current_player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    #1st guard
    for player in miwa_pool.q:
        if player.get_id() == current_player.id:
            raise HTTPException(status_code=400, detail="Oyunchu echak ele kutuu bolmosundo")
    
    #2nd guard
    exists = db.query(Match).filter(Match.status == "active", (current_player.id == Match.player1_id) | (current_player.id == Match.player2_id)).first()
    if exists is not None:
        raise HTTPException(status_code=400, detail="Oyunchu echak ele oyunda")
    
    
    player = WaitingPlayer(current_player, category)
    miwa_pool.enqueue(player)
    match = miwa_pool.try_pair()
    if match is None:
        return {"status":"searching", "message":"Kutuu bolmosuno koshtuk. Ataandash kutuudobuz."}
    else:
        return {"status":"match_found", "message":f"{match[1].player.username} menen oiun bashtaluuda."}