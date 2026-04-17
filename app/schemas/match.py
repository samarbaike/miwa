from pydantic import BaseModel

class BotMatch(BaseModel):

    bot_id: int
    category: str