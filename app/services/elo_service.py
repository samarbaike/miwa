class EloService:

    @staticmethod
    def calculate_new_ratings(winner_rank, loser_rank):
        expected_w = 1/(1 + 10**((loser_rank-winner_rank)/400))
        new_winner = round(winner_rank + 32*(1 - expected_w))

        expected_l = 1/(1 + 10**((winner_rank-loser_rank)/400))
        new_loser = round(loser_rank + 32*(0 - expected_l))
        
        return new_winner, new_loser
                      