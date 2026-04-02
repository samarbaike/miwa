from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.match_services import generate_room_code


router = APIRouter()

@router.post("/api/matches/create-invite")
def create_invited_match(db: Session=Depends(get_db)):
    code = generate_room_code()
    