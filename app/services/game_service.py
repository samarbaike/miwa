from fastapi import FastAPI
import asyncio
from sqlalchemy.orm import Session

from app.database import engine
from app.models.question import MultipleChoice
from app.core.events import WSEvents
from app.models.user import Player
from app.services.elo_service import EloService
from app.models.match import Match, MatchStatus

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
        self.answers_this_round: dict[int, dict] = {} 
        #player_id : {"answer" : answer,"timestamp" : timestamp}

        #to decide the winnder in case of equal scores
        self.answer_history: dict[int, list] = {
            player1_id : [],
            player2_id : []
        }

        #backround time tick
        self.question_timer_task: asyncio.Task | None = None 

        #to calculate time_taken in answer_history
        self.question_timer_start = None

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

        #start the timer
        self.question_timer_start = asyncio.get_event_loop().time()

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
            await asyncio.sleep(60)
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

    async def _resolve_question(self, app):
        #fetch question from db by current_question_index
        qid = self.question_ids[self.current_question_index]
        with Session(engine) as db:
            question = db.query(MultipleChoice).filter(MultipleChoice.id == qid).first()

        #calculating scores
        for player_id, data in self.answers_this_round.items():
            if data["answer"] is not None and data["answer"]==question.correct_answer:
                self.scores[player_id]+=1

                #storing time taken to answer
                time_taken = data["timestamp"] - self.question_timer_start
                self.answer_history[player_id].append(time_taken)

        #broadcasting results
        if self.answers_this_round[self.player2_id]['answer'] is not None:
            await app.state.room_manager.send_to(self.match_id, self.player1_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : f"Ataandash {self.answers_this_round[self.player2_id]['answer']} joobun belgildedi"
            })
        else:
            await app.state.room_manager.send_to(self.match_id, self.player1_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : f"Ataandash joob belgilebedi"
            })


        if self.answers_this_round[self.player1_id]['answer'] is not None:
            await app.state.room_manager.send_to(self.match_id, self.player2_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : f"Ataandash {self.answers_this_round[self.player1_id]['answer']} joobun belgildedi"
            })
        else:
            await app.state.room_manager.send_to(self.match_id, self.player2_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : f"Ataandash joob belgilebedi"
            })

        #advancing question index
        self.current_question_index+=1

        #stop/continue
        if self.current_question_index>=len(self.question_ids):
            await self._end_match(app)
        else: 
            await self.start_question(app)

    async def _end_match(self, app):

        if self.scores[self.player1_id] > self.scores[self.player2_id]:
            winner_id = self.player1_id
            loser_id = self.player2_id
        elif self.scores[self.player2_id] > self.scores[self.player1_id]:
            winner_id = self.player2_id
            loser_id = self.player1_id
        else:
            p1_time_taken = sum(self.answer_history[self.player1_id])
            p2_time_taken = sum(self.answer_history[self.player2_id])
            if p1_time_taken<p2_time_taken:
                winner_id = self.player1_id
                loser_id = self.player2_id
            elif p2_time_taken<p1_time_taken:
                winner_id = self.player2_id
                loser_id = self.player1_id
            else:
                #in case they are supppper equal
                winner_id = None
                loser_id = None
                with Session(engine) as db:
                    winner = db.query(Player).filter(Player.id == self.player1_id).first()
                    loser = db.query(Player).filter(Player.id == self.player2_id).first()

                    winner.total_matches += 1
                    loser.total_matches +=1

                    match = db.query(Match).filter(Match.id == self.match_id).first()
                    match.status = MatchStatus.COMPLETED
                    match.winner_id = None

                    db.commit()

                await app.state.room_manager.broadcast(self.match_id, {
                    "event":WSEvents.MATCH_ENDED,
                    "data":{
                        "status":"draw",
                        "score": self.scores[self.player2_id]
                    }
                })
                del app.state.active_games[self.match_id]
                return


        #calculating new ELO's
        with Session(engine) as db:
            winner = db.query(Player).filter(Player.id == winner_id).first()
            loser = db.query(Player).filter(Player.id == loser_id).first()
        
            result = EloService.calculate_new_ratings(winner.elo, loser.elo)
            
            #update the damn DB for both players
            winner.elo = result[0]
            winner.wins += 1
            winner.streak += 1
            winner.total_matches += 1

            loser.streak = 0
            loser.elo = result[1]
            loser.total_matches += 1

            #update DB for Match
            match = db.query(Match).filter(Match.id == self.match_id).first()
            match.status = MatchStatus.COMPLETED
            match.winner_id = winner_id

            db.commit()

        await app.state.room_manager.send_to(self.match_id, winner_id, {
            "event" : WSEvents.MATCH_ENDED,
            "data" : {
                "status":"win",
                "score" : self.scores[winner_id],
                "elo" : result[0]
            }
        })
        await app.state.room_manager.send_to(self.match_id, loser_id, {
            "event" : WSEvents.MATCH_ENDED,
            "data" : {
                "status":"lose",
                "score" : self.scores[loser_id],
                "elo" : result[1]
            }
        })

        del app.state.active_games[self.match_id]