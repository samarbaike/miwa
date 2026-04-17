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
                 question_ids: list[int],
                 is_bot_match = False):
        self.match_id = match_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.question_ids = question_ids  #id's of questions in the instance of this class
        self.is_bot_match = is_bot_match

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

        #for the Match model storage
        self.answers_data: dict[int, dict[int, dict]] = {}
        # answers_data = {player_id: {question_index: {"answer": answer,"time_taken": time_taken,"is_correct": bool0}}}
        
        #backround time tick
        self.question_timer_task: asyncio.Task | None = None 

        #to calculate time_taken in answer_history
        self.question_timer_start = None

        #fetching questions earlier to keep db sessions less
        with Session(engine) as db:
            questions = db.query(MultipleChoice)\
                .filter(MultipleChoice.id.in_(question_ids))\
                .all()

        # preserve order
        questions_map = {q.id: q for q in questions}
        self.questions = [questions_map[qid] for qid in question_ids]

    async def start_question(self, app):

        #fetch question from db by current_question_index
        question = self.questions[self.current_question_index]
            
        
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
        
        
        if timestamp is None:
            time_taken = 30
        else:
            time_taken = timestamp - self.question_timer_start

        if player_id not in self.answers_data:
            self.answers_data[player_id] = {}
        self.answers_data[player_id][self.current_question_index] = {
            "answer" : answer,
            "time_taken" : time_taken,
            "is_correct" : None
        }
        
        await app.state.room_manager.broadcast(self.match_id, {
            "event" : WSEvents.PLAYER_ANSWERED,
            "data" : {
                "player_id": player_id,
                "message": "Ataandash joop berdi"
                }
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
                self.answers_data[player_id][self.current_question_index]["is_correct"] = True
            else:
                self.answers_data[player_id][self.current_question_index]["is_correct"] = False


        #broadcasting results
        # player1
        if self.answers_this_round[self.player2_id]['answer'] is not None:
            await app.state.room_manager.send_to(self.match_id, self.player1_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : {
                    "correct_answer" : question.correct_answer,
                    "current_score" : self.scores[self.player1_id],
                    "opp_status" : f"Ataandash {self.answers_this_round[self.player2_id]['answer']} joobun belgildedi"
                    }
            })
        else:
            await app.state.room_manager.send_to(self.match_id, self.player1_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : {
                    "correct_answer" : question.correct_answer,
                    "current_score" : self.scores[self.player1_id],
                    "opp_status" : f"Ataandash joob belgilebedi"
                    }
            })

        # player2
        if self.answers_this_round[self.player1_id]['answer'] is not None:
            await app.state.room_manager.send_to(self.match_id, self.player2_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : {
                    "correct_answer" : question.correct_answer,
                    "current_score" : self.scores[self.player2_id],
                    "opp_status" : f"Ataandash {self.answers_this_round[self.player1_id]['answer']} joobun belgildedi"
                    }
            })
        else:
            await app.state.room_manager.send_to(self.match_id, self.player2_id, {
                "event" : WSEvents.QUESTION_RESULTS,
                "data" : {
                    "correct_answer" : question.correct_answer,
                    "current_score" : self.scores[self.player2_id],
                    "opp_status" : f"Ataandash joob belgilebedi"
                    }
            })

        #advancing question index
        self.current_question_index+=1

        #stop/continue
        if self.current_question_index>=len(self.question_ids):
            await self._end_match(app)
        else: 
            await self.start_question(app)

    def _determine_result(self):
        p1 = self.player1_id
        p2 = self.player2_id

        if self.scores[p1] > self.scores[p2]:
            return "win", p1, p2
        elif self.scores[p2] > self.scores[p1]:
            return "lose", p2, p1

        # tie-break by time (only correct answers)
        p1_time = sum(
            q["time_taken"]
            for q in self.answers_data[p1].values()
            if q["is_correct"]
        )
        p2_time = sum(
            q["time_taken"]
            for q in self.answers_data[p2].values()
            if q["is_correct"]
        )

        if p1_time < p2_time:
            return "win", p1, p2
        elif p2_time < p1_time:
            return "lose", p2, p1

        return "draw", None, None

    async def _end_match(self, app):
        # 1. Determine result
        result, winner_id, loser_id = self._determine_result()

        # 2. DB transaction (single session)
        with Session(engine) as db:
            match = db.query(Match).filter(Match.id == self.match_id).first()
            match.status = MatchStatus.COMPLETED
            match.answers_data = self.answers_data

            p1 = db.query(Player).filter(Player.id == self.player1_id).first()
            p2 = db.query(Player).filter(Player.id == self.player2_id).first()

            # BOT MATCH
            if self.is_bot_match:
                human = p1  # assuming player1 is human

                human.total_matches += 1

                if result == "win":
                    human.wins += 1
                    human.streak += 1
                elif result == "lose":
                    human.streak = 0
                elif result == "draw":
                    human.wins += 1
                    human.streak += 1  # keep your original logic

                match.winner_id = None

                db.commit()

                await app.state.room_manager.send_to(self.match_id, self.player1_id, {
                    "event": WSEvents.MATCH_ENDED,
                    "data": {
                        "status": result,
                        "score": self.scores[self.player1_id],
                        "progress": 0,
                        "comment": "Bottor menen oynoo ELO'nu kotorboit"
                    }
                })

                del app.state.active_games[self.match_id]
                return

            # DRAW (PvP)
            if result == "draw":
                p1.total_matches += 1
                p2.total_matches += 1
                match.winner_id = None

                db.commit()

                await app.state.room_manager.broadcast(self.match_id, {
                    "event": WSEvents.MATCH_ENDED,
                    "data": {
                        "status": "draw",
                        "score": self.scores[self.player1_id],
                        "progress": 0
                    }
                })

                del app.state.active_games[self.match_id]
                return

            # WIN / LOSE (PvP)
            winner = p1 if winner_id == self.player1_id else p2
            loser = p2 if winner_id == self.player1_id else p1

            result_elo = EloService.calculate_new_ratings(winner.elo, loser.elo)

            w_progress = result_elo[0] - winner.elo
            l_progress = result_elo[1] - loser.elo

            # update winner
            winner.elo = result_elo[0]
            winner.wins += 1
            winner.streak += 1
            winner.total_matches += 1

            # update loser
            loser.elo = result_elo[1]
            loser.streak = 0
            loser.total_matches += 1

            match.winner_id = winner_id

            db.commit()

        # 3. Send results (outside DB session)

        await app.state.room_manager.send_to(self.match_id, winner_id, {
            "event": WSEvents.MATCH_ENDED,
            "data": {
                "status": "win",
                "score": self.scores[winner_id],
                "progress": f"+{w_progress}",
                "elo": result_elo[0]
            }
        })

        await app.state.room_manager.send_to(self.match_id, loser_id, {
            "event": WSEvents.MATCH_ENDED,
            "data": {
                "status": "lose",
                "score": self.scores[loser_id],
                "progress": f"{l_progress}",
                "elo": result_elo[1]
            }
        })

        del app.state.active_games[self.match_id]