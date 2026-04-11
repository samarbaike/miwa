from fastapi import FastAPI
import asyncio
from sqlalchemy.orm import Session

from app.database import engine
from app.models.question import MultipleChoice
from app.core.events import WSEvents
from app.models.user import Player

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

    async def start_question(self, app):

        #fetch question from db by current_question_index
        qid = self.question_ids[self.current_question_index]
        with Session(engine) as db:
            question = db.query(MultipleChoice).filter(MultipleChoice.id == qid).first()
            
        
        #reset www answered for upcoming question
        self.answers_this_round = {}

        #check background timer
        if self.question_timer_task is not None:
            self.question_timer_task.cancel()
            self.question_timer_task = None

        #broadcasting question to players
        await app.state.room_manager.broadcast(self.match_id, {
            "event":WSEvents.QUESTION_START,
            "data": {
                "q_index":self.current_question_index,
                "q_text":question.body,
                "q_options":question.options
            }
        })

        #starting fresh TIMER task
        self.question_timer_task = asyncio.create_task(self._question_timer(app))


    async def _question_timer(self, app):
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            return
        

        for pid in [self.player1_id, self.player2_id]:
            if pid not in self.answers_this_round:
                await self.handle_answer(pid, None, None, app)

    async def handle_answer(self, player_id, answer, timestamp, app):
        if player_id in self.answers_this_round:
            return
        
        self.answers_this_round[player_id] = {
            "answer" : answer,
            "timestamp" : timestamp
        }
          
        
        await app.state.room_manager.broadcast(self.match_id, {
            "event" : WSEvents.PLAYER_ANSWERED,
            "data" : "Ataandash joop berdi"
        })

        if len(self.answers_this_round) == 2:
            self.question_timer_task.cancel()
            await self._resolve_question(app)