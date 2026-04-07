from app.models.user import Player
import datetime
from collections import deque


class WaitingPlayer:
    def __init__(self, player, category, time_joined=None, elo_window=15):
        self.player = player
        self.category = category
        self.elo_window = elo_window
        if time_joined is None:
            self.time_joined = datetime.datetime.now(datetime.UTC)
        self.time_joined = time_joined

    def expand_elo_window(self):
        self.elo_window+=5

    #getter_method
    def get_id(self) -> int:
        return self.player.id

class MatchmakingPool:
    def __init__(self):
        self.q = deque() #queue

    def enqueue(self, waiting_player):
        self.q.append(waiting_player)

    def dequeue(self, player_id: int):
        for player in self.q:
            if player_id == player.get_id():
                self.q.remove(player)
                return True
        return False
       
    def try_pair(d: deque):
        if len(d)<2:
            return None
        
        for A, B in d:
            if abs(A.elo - B.elo) <= A.window and abs(A.elo - B.elo) <= B.elo_window:

    def tick(d: deque):
        waiting_player.expand_elo_window(d)