import random
import string
from app.models.match import Match

class MatchService:
    
    @staticmethod
    def _generate_room_code(length=6):
        pool = string.ascii_uppercase + string.digits
        return ''.join(random.choice(pool) for _ in range(length))

    @staticmethod
    def create_invite_match(db, user_id):
        room_code = MatchService._generate_room_code()
        new_invite_match = Match(player1_id=user_id,
                                 status="WAITING",
                                 invite_code=room_code)
        db.add(new_invite_match)
        db.commit()
        db.refresh(new_invite_match)

        return room_code