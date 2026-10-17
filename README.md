# Miwa

Miwa is a real-time multiplayer quiz platform for preparing for the ОРТ, the national standardized test required for university admission in Kyrgyzstan. Players compete against each other in live matches across three sections: math, grammar, and vocabulary.

> **Status:** under active development.

## Features

- **Real-time multiplayer:** live head-to-head quiz sessions over WebSockets
- **Matchmaking:** pairs players into matches
- **Bot / GhostEngine flows:** handles matches that need a simulated opponent
- **Three quiz sections:**
  - **Math:** practice questions in the ОРТ format
  - **Grammar:** practice questions in the ОРТ format
  - **Vocabulary:** Kyrgyz-language word-meaning battles (see below)

## Vocabulary mode

The vocabulary section replaces the ОРТ's analogy section. Analogy questions ask test-takers to pair words by their relation, which requires knowing what the words mean. Many students struggle with them because of gaps in vocabulary, not because of weak reasoning.

In Miwa, players compete by:

- finding the meaning of a given word, or
- finding the word that matches a given meaning.

This mode targets the **Kyrgyz language**, even though many ОРТ test-takers take the test in Russian.

## Tech stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI |
| Real-time communication | WebSockets |
| Language | Python |
| Database | PostgreSQL (hosted on Supabase), accessed through SQLAlchemy |
| Frontend / client | Planned: vanilla HTML, CSS and JavaScript (see [Roadmap](#roadmap)) |

## Architecture

Miwa is organized around a few core components:

- **API layer (FastAPI):** serves the HTTP endpoints for the application.
- **WebSocket layer:** keeps a persistent connection with each player so match events can be exchanged in real time.
- **Matchmaking:** takes players who want to play and groups them into matches.
- **Bot / GhostEngine:** provides the bot flows used when a match involves a simulated opponent.

### How a match flows

1. **Log in.** The player logs in over HTTP and receives a session cookie, which protects the REST routes.
2. **Join the queue.** The player opens the lobby socket (`/ws/lobby/{player_id}`) and calls `POST /api/matchmaking/join?category=...`, which adds them to the `MatchmakingPool`.
3. **Pairing.** A background task runs every 10 seconds. Each tick widens every waiting player's ELO window by 5 (it starts at ±15), then pairs two players of the same category if each one falls inside the other's window. The server creates a `Match` with 10 random questions from that category and sends `match_found` with the match ID through the lobby socket.
4. **Playing.** Both players connect to `/ws/match/{match_id}/{player_id}` and send `join_match`. The server broadcasts `player_joined`, and once both are connected a `GameService` is created for the match and sends `question_start`. Each `submit_answer` triggers a `player_answered` message for the opponent, without revealing the choice. When both players have answered, or the server-side 30-second timer runs out, the server sends `question_results` and moves on to the next question.
5. **Finishing.** After the last question the server sends `match_ended`. The winner is the player with more correct answers, and ties are broken by total time on correct answers. ELO, wins, streak and total matches are updated, and the answers are saved on the match record.
6. **Playing a bot.** If no opponent is found after 60 seconds, the server sends a `bot_offer`. The player can list the bots (`GET /api/bots`) and switch to one (`POST /api/matchmaking/switch-to-bot`). In a bot match, `GhostEngine` takes the place of the second player: for each question it looks up the bot's recorded `performance_data`, waits the recorded response time, and submits the recorded answer through the same path a human answer takes. If the bot has `advice_data` for that question, the hint is sent to the human. For questions the bot has no recording for, it falls back to a short random delay and a random answer. Bot matches don't change ELO.

Event names are defined in one place, `app/core/events.py` (`WSEvents`), so a typo fails immediately instead of silently.

## Getting started

```bash
# clone the repository
git clone https://github.com/samarbaike/miwa.git
cd miwa

# create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# install dependencies
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary python-dotenv \
    "passlib[bcrypt]" "bcrypt==4.0.1" pytz "pydantic[email]"

# run the development server
uvicorn app.main:app --reload
```

`bcrypt` is pinned to 4.0.1 because newer releases are incompatible with `passlib` and break password hashing. A pinned `requirements.txt` is on the [roadmap](#roadmap).

### Configuration

Create a `.env` file in the project root (it is git-ignored) with the database credentials. All five variables are required, and the app will not start without them:

```
user=<database user>
password=<database password>
host=<database host>
port=<database port>
dbname=<database name>
```

The app connects to PostgreSQL over SSL and creates the tables automatically on startup.

### Adding questions and bots

There is no admin interface yet. Questions and ghost-bot profiles are inserted directly into the database, for example with `psql`.

- **`multiple_choice` table:** `body`, `options` (a JSON list of answer options), `correct_answer` (the index of the correct option), `category`, and an optional `image`. The `category` sent to `POST /api/matchmaking/join` must match the `category` stored on the questions.
- **`bots` table:** `botname`, `backstory`, `performance_data` and `advice_data` (both JSON). `performance_data` maps question IDs to a recorded answer, for example `{"12": {"answer_index": 2, "time_ms": 4200}}`, and `advice_data` maps question IDs to a hint string. An empty `{}` is valid for both.

### Trying it out

Open `http://127.0.0.1:8000/docs` to test the REST endpoints. WebSockets can't be tested from `/docs`: use the browser console's `WebSocket` API or [websocat](https://github.com/vi/websocat).

## Project structure

```
miwa/
├── app/
│   ├── main.py                 # creates the app; sets up the pool, managers and active games
│   ├── database.py             # SQLAlchemy engine and sessions, reads credentials from .env
│   ├── room_manager.py         # RoomManager: WebSocket connections for each match
│   ├── global_manager.py       # GlobalManager: lobby sockets (match_found, bot_offer)
│   ├── core/
│   │   ├── dependencies.py     # get_current_player: session-cookie authentication
│   │   ├── events.py           # WSEvents: WebSocket event name constants
│   │   └── security.py         # password hashing (bcrypt)
│   ├── models/                 # database tables: users, matches, questions, bots, sessions
│   ├── schemas/                # Pydantic request and response schemas
│   ├── services/               # business logic
│   │   ├── auth_service.py     # register and login
│   │   ├── elo_service.py      # ELO rating calculation
│   │   ├── match_service.py    # invite matches and room codes
│   │   ├── matchmaking_service.py  # WaitingPlayer and MatchmakingPool
│   │   ├── run_mm_service.py   # background matchmaking loop
│   │   ├── game_service.py     # GameService: live state of one match
│   │   └── bot_service.py      # GhostEngine
│   └── routes/                 # thin FastAPI routers: auth, user, matches, ws
├── docs/
│   └── rest_checklist.md       # REST endpoint smoke-test checklist
├── miwa_roadmap_v5.txt         # the full day-by-day development plan
└── websocat                    # command-line WebSocket client for testing
```

## Roadmap

Items are checked off when they exist in the code. The full day-by-day plan is in [`miwa_roadmap_v5.txt`](miwa_roadmap_v5.txt).

**WebSocket layer**

- [x] Connection managers: `RoomManager` (sockets per match) and `GlobalManager` (lobby sockets)
- [x] WebSocket event name constants in `app/core/events.py`
- [x] Match and lobby WebSocket endpoints
- [x] Matchmaking pool with an expanding ELO window and a background tick

**Game loop**

- [x] `GameService`: live state of one match, with a server-side 30-second question timer
- [x] `join_match`, `question_start`, `submit_answer` and `question_results` flow
- [x] `match_ended`: winner and tie-break, ELO and stats update, answers stored on the match
- [ ] End-to-end two-player test, including edge cases (disconnects, simultaneous answers), with findings in `docs/known_issues.md`
- [ ] `docs/websocket_protocol.md`: every event, its payload, who sends it and what happens next

**Ghost bot**

- [x] `GhostEngine` replaying recorded answers and response times, with optional advice
- [x] Bot offer after 60 seconds in the queue, and the switch-to-bot flow
- [ ] Deterministic fallback for questions the bot has no recording for (currently a short random delay and a random answer)
- [ ] Seeding script to fill `performance_data` and `advice_data` from real players' historical matches

**Match modes**

- [x] Ranked
- [ ] Invite (private room code): the REST endpoints exist, starting the game over WebSockets is still to do
- [ ] Practice: solo play with no ELO change

**Frontend (vanilla HTML, CSS and JavaScript)**

- [ ] Login and register, home, leaderboard and profile pages
- [ ] Matchmaking page: waiting screen, ELO window display, redirect on `match_found`
- [ ] Battle page: question with optional image, countdown, opponent status, results and end-of-match overlay
- [ ] Mode selector (Ranked, Practice, Invite)

**Deployment and hardening**

- [ ] Move the remaining hard-coded settings (session expiry, ELO constants) to environment variables, add `.env.example` and CORS middleware, and pin versions in `requirements.txt`
- [ ] Deploy (Render or Railway) with a hosted PostgreSQL database, and add the public URL to this README
- [ ] Error-handling audit (clean JSON for 400, 401, 404 and 409) and structured logging
- [ ] Testing with real users, recorded in `docs/user_testing_log.md`

**Documentation and polish**

- [ ] API endpoint table and WebSocket event table in this README
- [ ] `CONTRIBUTING.md`: adding a question category, a ghost bot profile and a WebSocket event
- [ ] Design document: UML class diagram, OOP concept map and architecture notes
- [ ] Match history and streak edge cases on the profile page