import datetime
from collections import deque


class WaitingPlayer:
    def __init__(self, player, category, time_joined=None, elo_window=15, bot_offer_sent: bool = False):
        self.player = player
        self.category = category
        self.elo_window = elo_window
        self.bot_offer_sent = bot_offer_sent
        if time_joined is None:
            self.time_joined = datetime.datetime.now(datetime.UTC)
        else: 
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
       
    def try_pair(self):
        if len(self.q)<2:
            return None
        
        A = self.q[0]
        for B in list(self.q)[1:]:
            if abs(A.player.elo - B.player.elo) <= A.elo_window and abs(A.player.elo - B.player.elo) <= B.elo_window and A.category == B.category:
                self.q.remove(A)
                self.q.remove(B)
                return (A, B)
        return None
    
    def tick(self):
        for player in list(self.q):
            player.expand_elo_window()