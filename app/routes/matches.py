from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.match_service import MatchService
from app.core.dependencies import get_current_player
from app.models.user import Player
from app.models.match import Match, MatchStatus, MatchMode
from app.services.matchmaking_service import WaitingPlayer

router = APIRouter()

@router.post("/api/matches/create-invite")
def create_invited_match(db: Session=Depends(get_db), 
                         current_player: Player=Depends(get_current_player) ):
    room_code = MatchService.create_invite_match(db, current_player.id)
    return {"room_code":room_code}

@router.post("/api/matches/join-invite")
def join_bycode(room_code: str,
                db: Session = Depends(get_db),
                current_player: Player = Depends(get_current_player)):
    
    match = db.query(Match).filter(Match.mode==MatchMode.INVITE, Match.invite_code==room_code).first()
    if match is None:
        raise HTTPException(status_code=400, detail="Myndai kodd menen ec kandai oyun jok")

    if current_player.id == match.player1_id:
        raise HTTPException(status_code=400, detail="Siz ozunuzdun oyunga ozunuz koshula albaisyz")
        
    match.player2_id = current_player.id
    match.status = MatchStatus.IN_PROGRESS
    db.commit()
    db.refresh(match)

    return match


@router.get("/api/match/{id}")
def get_match_status(id: int, db: Session=Depends(get_db)):
    match = db.query(Match).filter(Match.id == id).first()
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match not found")
    return match

@router.post("/api/matchmaking/join")
def matchmaking(request: Request,
                category: str, 
                current_player: Player = Depends(get_current_player), 
                db: Session = Depends(get_db)):
    
    #initializing MatchmakingPool from app.state
    pool = request.app.state.pool

    #1st guard
    for player in pool.q:
        if player.get_id() == current_player.id:
            raise HTTPException(status_code=400, detail="Oyunchu echak ele kutuu bolmosundo")
    
    #2nd guard
    exists = db.query(Match).filter(Match.status == MatchStatus.IN_PROGRESS, 
                                    (current_player.id == Match.player1_id) | (current_player.id == Match.player2_id)).first()
    if exists is not None:
        raise HTTPException(status_code=400, detail="Oyunchu echak ele oyunda")
    
    
    player = WaitingPlayer(current_player, category)
    pool.enqueue(player)

    return {"status":"searching", 
            "message":"Kutuu bolmosuno koshtuk. Ataandash kutuudobuz."}


@router.post("/api/matchmaking/cancel")
def cancel(request: Request,
           current_player: Player = Depends(get_current_player)):
    
    pool = request.app.state.pool

    delete = pool.dequeue(current_player.id)
    if not delete:
        raise HTTPException(status_code=400, detail="Oyunchu kutuu bolmosundo emes")
    
    return {
        "status":"success",
        "message":"Kutuu bolmusunon chygaryldynyz"
    }

