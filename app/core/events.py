class WSEvents:
    """when referencing these events in other routes files, 
    use WSEvents.X to avoid typo"""

    JOIN_MATCH      = "join_match"
    PLAYER_JOINED   = "player_joined"
    MATCH_UPDATE    = "match_update"
    QUESTION_START  = "question_start"
    SUBMIT_ANSWER   = "submit_answer"
    PLAYER_ANSWERED = "player_answered"
    QUESTION_RESULTS = "question_results"
    MATCH_ENDED     = "match_ended"
    MATCH_FOUND     = "match_found"