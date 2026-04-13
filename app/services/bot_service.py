from app.models.bot import Bot
import asyncio
import random

class GhostEngine:
    def __init__(self, bot: Bot, question_ids: list):
        self.bot = bot
        self.question_ids = question_ids
        self.bot_questions = {k: bot.performance_data[f"{k}"] for k in question_ids if str(k) in bot.performance_data}
        # {12: {"answer_index": 2, "time_ms": 4200}}
        
    async def answer_question(self, question_id, match_id, player_id, app):
        if question_id in self.bot_questions:
            bot_data = self.bot_questions[question_id]
            await asyncio.sleep(bot_data["time_ms"]/1000)

            if str(question_id) in self.bot.advice_data:
                await app.state.room_manager.send_to(match_id, player_id, {
                     "advice": self.bot.advice_data[str(question_id)]
                     })
                
            return bot_data["answer_index"]
        
        else:
            await asyncio.sleep(random.uniform(2,6))
            return random.randint(0, 3)