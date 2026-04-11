from fastapi import FastAPI
import asyncio
from sqlalchemy.orm import Session

from app.database import engine
from app.models.question import MultipleChoice
from app.core.events import WSEvents

app = FastAPI()

class GameService:

    """one instance of this class is a active match in app.state.active_games[match_id]
    This class controls what is happening in that active game, who scored what, which questions
    are asked"""

    def __init__(self, 
                 match_id: int,
                 player1_id: int, 
                 player2_id: int, 
                 question_ids: list[int]):
        self.match_id = match_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.question_ids = question_ids  #id's of questions in the instance of this class
        
        #the index of question with which game_service is dealing
        self.current_question_index = 0 #starting question will have 0
        
        #to manage player score
        self.scores: dict[int, int] = {    
             player1_id:0,
             player2_id:0
        }

        #to manage who, what, when answered for specific question
        self.answers_this_round: dict[int, dict] = {} #player_id : [answer, timestampt]

        #backround time tick
        self.question_timer_task: asyncio.Task | None = None 
