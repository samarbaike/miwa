# The Argon Method: Glass-Box Engineering for Miwa

> **Who this is for:** You already know Python functions, classes/OOP, and imports—and as an Applied Mathematics & Informatics student, you think in terms of state, inputs/outputs, and data structures. You didn't suddenly "stop knowing Python." What happened is that **frameworks invert control** and hide execution behind decorators, dependency injection, ORMs, and event loops.
>
> **Why `miwa_roadmap_v5.txt` stopped working:** The roadmap organized your work **horizontally by architectural layer** (Day 2: all Models $\rightarrow$ Day 3: all Schemas $\rightarrow$ Day 7: all Routes $\rightarrow$ Day 11: Matchmaking $\rightarrow$ Day 14: WebSockets $\rightarrow$ Week 4: all Frontend). Horizontal building works when an AI gives you the blueprint, because each file is small in isolation. But by Week 3, you have **24 files across 6 layers** (`models`, `schemas`, `services`, `routes`, `core`, `managers`) talking to each other invisibly. You can see the *bricks*, but the *mortar* (how FastAPI, SQLAlchemy, and `asyncio` wire them together at runtime) is hidden inside the frameworks.

---

## Part 1: Diagnosis — Why Frameworks Feel Like a Different Language

In standard Python (what you already know), **you call the code**:
```python
# Standard Python: You are in control of the main loop
db = connect_to_database()
player = get_player(db, cookie="abc-123")
room_code = MatchService.create_invite_match(db, player.id)
print({"room_code": room_code})
db.close()
```

In FastAPI + SQLAlchemy (what is in `/miwa`), **the framework calls your code** (Inversion of Control):
```python
# app/routes/matches.py (Lines 19-23)
@router.post("/api/matches/create-invite")
def create_invited_match(
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    room_code = MatchService.create_invite_match(db, current_player.id)
    return {"room_code": room_code}
```

When you look at `create_invited_match`, your brain asks:
1. **Who called `create_invited_match`?** (You never called it anywhere in `app/main.py`!)
2. **Why is `db: Session = Depends(get_db)` in the default argument?** In normal Python, default arguments evaluate *once* when the file is imported. Why does `get_db()` use `yield` instead of `return`?
3. **Where did `request.app.state.pool` come from?** Why are some data structures in PostgreSQL (`Match`, `Player`) and others in Python RAM (`app.state.pool`, `app.state.active_games`, `app.state.room_manager`)?
4. **How does `Player.email == user_in.email` inside `session.query(Player).filter(...)` not just evaluate to `False` in Python?**

Until you strip away that "framework magic" and see the raw Python underneath, adding more features will only increase the fog. **The Argon Method** replaces horizontal checklist coding with **4 core practices**:
1. **The De-Sugaring Translation** (Translating FastAPI/SQLAlchemy magic into plain OOP Python)
2. **The Two-Brain State Map** (RAM vs. Database mental model)
3. **The Vertical Packet Trace** (Tracing one feature top-to-bottom before touching code)
4. **Vertical Slice Completion + Bug Hunting** (Finding and fixing the real bugs hiding in your existing code as your learning exercises)

---

## Part 2: De-Sugaring the 4 Hidden Mechanisms in `/miwa`

Before writing another line of code, anchor these four translations to the Python you already know.

### 1. FastAPI Decorators & `Depends()` $\rightarrow$ Higher-Order Functions & Generators

When you write `@router.post("/api/matches/create-invite")` and `Depends(get_current_player)`, FastAPI is just building a **dictionary of functions** and running a **wrapper function** when an HTTP text string arrives over a TCP socket.

Here is what FastAPI actually runs under the hood when a request hits `/api/matches/create-invite` (referencing `app/database.py` and `app/core/dependencies.py`):

```python
# WHAT FASTAPI EXECUTES UNDER THE HOOD FOR ONE REQUEST:
def fastapi_handle_http_request(raw_http_request):
    # 1. Start the generator in app/database.py: get_db()
    db_generator = get_db()
    db = next(db_generator)  # Runs up to `yield db` (Line 27 of app/database.py)

    try:
        # 2. Extract the "session_id" cookie from the HTTP header
        cookie_val = raw_http_request.cookies.get("session_id", None)

        # 3. Call your dependency in app/core/dependencies.py
        current_player = get_current_player(session_id=cookie_val, db=db)

        # 4. Call your actual route function in app/routes/matches.py
        result_dict = create_invited_match(db=db, current_player=current_player)

        # 5. Convert Python dict/Pydantic model -> JSON string -> HTTP 200 response
        return to_http_json_response(result_dict, status=200)

    except HTTPException as exc:
        return to_http_json_response({"detail": exc.detail}, status=exc.status_code)

    finally:
        # 6. Resume get_db() after `yield` so `finally: db.close()` (Line 29) ALWAYS runs!
        try:
            next(db_generator)
        except StopIteration:
            pass
```

> **Key Takeaway:** `get_db()` uses `yield` instead of `return` because FastAPI pauses `get_db()` at line 27 (`yield db`), hands `db` to your route, waits for your route to finish (or crash), and then resumes `get_db()` at line 29 (`db.close()`) so you never leak database connections.

---

### 2. SQLAlchemy ORM $\rightarrow$ Operator Overloading & the Unit of Work Pattern

In `app/services/auth_service.py` (Line 15), you wrote:
```python
existing_user = session.query(Player).filter(Player.email == user_in.email).first()
```

In normal Python, comparing a class attribute `Player.email` (which is a `Column` object) to a string `"samar@example.com"` would return `False`. Why doesn't it?

Because SQLAlchemy overrides the `__eq__` magic method on `Column`!
* **`Player.email == user_in.email`** does **not** return a `bool`. It returns a SQL expression object (`BinaryExpression`) that represents the string `"players.email = :email_1"`.
* **`.filter(...)`** appends that expression to a query builder object in Python memory (no network call yet!).
* **`.first()`** is the trigger that actually compiles the Python objects into a SQL string (`SELECT * FROM players WHERE players.email = 'samar@example.com' LIMIT 1`), sends it over the network to Supabase PostgreSQL, receives the raw tuple row back, and instantiates a `Player(...)` Python object for you.

And what are `session.add()`, `session.commit()`, and `session.refresh()` in `auth_service.py` (Lines 22–24)?
* **`new_player = Player(...)`**: Creates a normal Python object in RAM. **`new_player.id` is `None`** right now because PostgreSQL generates the `id`, and we haven't talked to PostgreSQL yet.
* **`session.add(new_player)`**: Puts `new_player` into SQLAlchemy's in-memory staging area (like `git add`). Still no SQL sent!
* **`session.commit()`**: Opens a transaction, sends `INSERT INTO players ...`, and commits it permanently (like `git commit + push`).
* **`session.refresh(new_player)`**: Queries PostgreSQL for the newly generated `id` and `created_at` timestamp and populates `new_player.id` in Python RAM so `return new_player` passes Pydantic's `UserResponse(id: int = Field(gt=0))` check!

---

### 3. Pydantic (`app/schemas/`) vs. SQLAlchemy (`app/models/`) $\rightarrow$ The Bouncer vs. The Vault

Why do you have both `app/models/user.py` (`Player`) and `app/schemas/user.py` (`UserRegister`, `UserResponse`)?
* **SQLAlchemy Model (`Player`) = The Database Vault Row.** It holds `password_hash`, `is_premium`, internal IDs, and is tied to a live database `Session`. If you returned `Player` directly without filtering, you would leak `password_hash` to anyone calling `/api/user/{id}`!
* **Pydantic Schema (`UserRegister`, `UserResponse`) = The Club Bouncer at the Door.**
  * On the way **in** (`user_data: UserRegister`), Pydantic parses raw JSON strings, verifies `len(password) >= 8` and `EmailStr` format, and rejects bad data with HTTP `422` before your code even runs.
  * On the way **out** (`response_model=UserResponse` in `app/routes/auth.py`, Line 13), FastAPI takes your SQLAlchemy `Player` object, reads **only** `id`, `username`, `email`, and `elo`, strips out `password_hash`, and serializes it to JSON.

---

### 4. `asyncio`, `app.state`, and WebSockets $\rightarrow$ One Chef, Many Stoves

Why does `app/main.py` (Lines 16–25) have `lifespan(app)` and `app.state`?

* **HTTP is stateless and forgetful:** Every `POST` or `GET` request creates a fresh `db` session (`get_db`), does its job in ~20ms, and forgets everything when it returns.
* **Matchmaking and Live Battles are stateful and continuous:** If Player 1 joins the queue at `t=0s` and Player 2 joins at `t=4s`, the server must remember Player 1 in RAM between HTTP requests. And during a live 1v1 match, both players need an open two-way pipe (`WebSocket`) so the server can push `question_start` and `player_answered` at any millisecond without waiting for the browser to ask.

Here is the exact **Two-Brain Architecture** of your Miwa backend right now:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI SERVER PROCESS (RAM)                        │
│              Created ONCE at startup in `app/main.py:lifespan`             │
│                                                                            │
│  1. app.state.pool (MatchmakingPool)                                       │
│     └── deque([WaitingPlayer(p1, elo_window=15), ...])                     │
│                                                                            │
│  2. app.state.global_manager (GlobalManager)                               │
│     └── active_players: { player_id: WebSocket }  (/ws/lobby/{player_id})  │
│                                                                            │
│  3. app.state.room_manager (RoomManager)                                   │
│     └── active_connections: { match_id: { player_id: WebSocket } }         │
│                                                                            │
│  4. app.state.active_games (dict[int, GameService])                        │
│     └── { match_id: GameService(scores, current_question_index, timer) }   │
│                                                                            │
│  5. Background Loop: `run_matchmaking(app)`                                │
│     └── wakes up every 10s (`await asyncio.sleep(10)`), ticks windows,     │
│         pairs players, writes Match to DB, pings GlobalManager             │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │ SQL over SSL (psycopg2)
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     SUPABASE POSTGRESQL DATABASE (DISK)                    │
│              Permanent truth across server restarts (`app/models/`)        │
│                                                                            │
│  • players (id, username, email, password_hash, elo, wins, streak)         │
│  • sessions (session_token, player_id, expires_at)                         │
│  • multiple_choice (id, body, options, correct_answer, category)           │
│  • matches (id, player1_id, player2_id, status, mode, questions_data, ...) │
│  • bots (id, botname, backstory, performance_data, advice_data)            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: The Argon Learning Loop (Your Daily Method)

To finish Miwa and deeply understand every line of it, stop adding files horizontally. Instead, use this **4-Step Loop** for every session:

### Step 1: The "No-Code" Packet Trace (10 Minutes)
Before writing or editing any feature, open a blank scratchpad (or paper) and trace a single user action from Browser $\rightarrow$ Route $\rightarrow$ Dependency $\rightarrow$ Service $\rightarrow$ RAM/DB $\rightarrow$ Response **using exact file names and variable names**.
* *Rule:* If you cannot trace what happens to a variable from the moment it leaves the browser to the moment it hits PostgreSQL or `app.state`, **do not write code yet**. Read the files in that path first.

### Step 2: The "Break & Observe" Probe (15 Minutes)
Frameworks hide execution, so **force them to talk to you**:
1. Put a `print(f"[TRACE] function_name: {variable=}")` at each boundary (Route entry, Dependency check, Service method, WebSocket `receive_json()`).
2. Trigger the endpoint from `/docs`, `websocat`, or the browser, and watch the terminal output in real time.
3. Ask yourself: *"Did the lines print in the exact order I predicted in Step 1?"*

### Step 3: Build One Vertical Slice at a Time (60–90 Minutes)
Instead of "build all frontend HTML today, all CSS tomorrow, all JS on Friday," build **one vertical slice** end-to-end (Frontend UI $\leftrightarrow$ `fetch()` / `WebSocket` $\leftrightarrow$ FastAPI Route $\leftrightarrow$ Service $\leftrightarrow$ DB).
* When Slice 1 (e.g., Login/Register + `/api/user/me`) works visually in your browser and updates Supabase, your brain gets a complete, closed feedback loop.

### Step 4: The Rubber-Duck Commit Log (10 Minutes)
Before running `git commit`, write a 3-bullet explanation (in a personal `LEARNING_LOG.md` or commit body):
1. **What moved where?** (e.g., *"Cookie `session_id` traveled from browser header $\rightarrow$ `get_current_player` $\rightarrow$ queried `sessions` table."* )
2. **What lived in RAM vs. Disk?**
3. **What bug or edge case did I uncover and fix?**

---

## Part 4: Forensic Audit of `/miwa` — Learn by Fixing Your Own Codebase First!

The fastest way to master your existing backend before connecting the frontend is to **hunt down the real architectural bugs currently hiding in `/miwa`**. Because the codebase grew quickly across many files, several pieces don't quite line up.

Working through these **6 Real Bugs in `/miwa`** is your **Phase 1 Mastery Lab**. For each one, open the file, trace why it happens, and fix it yourself:

### Lab 1: The Invite Match Crash (Missing `questions_data`)
* **Where to look:** Compare `app/services/run_mm_service.py` (Lines 30–39) with `app/services/match_service.py` (Lines 13–23) and `app/routes/matches.py` (Lines 25–42), then trace into `app/routes/ws.py` (Lines 55–60) and `app/services/game_service.py` (Lines 58–65).
* **The Question to Answer:** When two players are matched by `run_matchmaking`, `new_match.questions_data` is populated with 10 random question IDs (`q_ids`). What is `new_invite_match.questions_data` set to when `MatchService.create_invite_match()` creates an invite match, or when Player 2 calls `/api/matches/join-invite`?
* **What happens at runtime:** When both invite players connect to `/ws/match/{match_id}/{player_id}`, line 57 of `ws.py` reads `q_ids = q.questions_data` (which is `None`!), passes `None` into `GameService(..., question_ids=None)`, and crashes on line 60 of `game_service.py` (`MultipleChoice.id.in_(None)`)!
* **What you learn by fixing it:** How data saved in PostgreSQL during an HTTP request (`POST /api/matches/join-invite`) is later hydrated into RAM (`GameService`) during a WebSocket connection.

### Lab 2: The Leaderboard Password-Hash Leak
* **Where to look:** `app/routes/user.py` (Lines 26–29):
  ```python
  @router.get("/api/leaderboard")
  def get_leaderboard(db: Session = Depends(get_db)):
      top_20 = db.query(Player).order_by(Player.elo.desc()).limit(20).all()
      return top_20
  ```
* **The Question to Answer:** Look at `@router.get("/api/user/{user_id}", response_model=UserResponse)` right above it on line 12, and then look at `@router.get("/api/leaderboard")` on line 26. Notice what is missing on line 26?
* **What happens at runtime:** Without `response_model=list[UserResponse]`, FastAPI serializes every column of the SQLAlchemy `Player` object directly to JSON—including every top player's `password_hash` and `email`!
* **What you learn by fixing it:** Why Pydantic `response_model` is an active security filter, not just documentation.

### Lab 3: The Duplicate Username Crash (`IntegrityError` vs `HTTPException`)
* **Where to look:** `app/services/auth_service.py` (Lines 14–28) and `app/models/user.py` (Lines 10–11).
* **The Question to Answer:** In `BaseUser` (`app/models/user.py`), **both** `username` and `email` have `unique=True`. In `AuthService.register()`, you check `filter(Player.email == user_in.email).first()`, but what happens if a new user registers with a new email and an **already-existing `username`**?
* **What happens at runtime:** `existing_user` is `None`, so your code runs `session.commit()`, and PostgreSQL throws a raw `sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint "players_username_key"`, crashing the request with a `500 Internal Server Error`!
* **What you learn by fixing it:** How database constraints (`unique=True` in SQLAlchemy/PostgreSQL) interact with service-layer validation (`(Player.email == ...) | (Player.username == ...)`).

### Lab 4: The Ghost Bot Foreign Key / Player Lookup Bug
* **Where to look:** `app/routes/matches.py` (Lines 131–137) and `app/services/game_service.py` (Lines 261–266).
* **The Question to Answer:** Look closely at `app/models/match.py` (Lines 20–22): `Match` has `player1_id`, `player2_id`, AND `player2_bot_id`. Now look at `app/routes/matches.py` (Line 133): when creating a bot match, it sets `player2_id=bot.id` instead of `player2_bot_id=bot.id`. And in `game_service.py` (Line 262), `_end_match` runs `p2 = db.query(Player).filter(Player.id == self.player2_id).first()`, querying the `players` table using a `bot.id`!
* **What you learn by fixing it:** How polymorphic/nullable relationships work in relational databases (`player2_id` vs `player2_bot_id`) and how `GameService` separates human persistence from bot simulation.

### Lab 5: The Matchmaking Queue Starvation Bug
* **Where to look:** `app/services/matchmaking_service.py` (Lines 37–47):
  ```python
  def try_pair(self):
      if len(self.q) < 2:
          return None
      A = self.q[0]
      for B in list(self.q)[1:]:
          if ...:
              return (A, B)
      return None
  ```
* **The Question to Answer:** Suppose Player 1 (`self.q[0]`) wants category `"Math"` (ELO 1500), Player 2 (`self.q[1]`) wants `"Grammar"` (ELO 110), and Player 3 (`self.q[2]`) wants `"Grammar"` (ELO 115). What does `try_pair()` do?
* **What happens at runtime:** `try_pair()` **only ever checks `A = self.q[0]` against everyone else!** Because `self.q[0]` (`"Math"`) doesn't match Player 2 or Player 3 (`"Grammar"`), `try_pair()` returns `None`—so Player 2 and Player 3 never get paired with each other as long as Player 1 is sitting at index `0`!
* **What you learn by fixing it:** This connects your DAA coursework directly to your backend! A nested loop over `i` and `j` (checking all pairs in the queue, not just index `0`) fixes head-of-line blocking.

### Lab 6: The `GhostEngine` Advice Crash (`NoneType`) & Fallback Rule
* **Where to look:** `app/services/bot_service.py` (Lines 9 and 17) and `app/models/bot.py` (Line 13).
* **The Question to Answer:** In `Bot` (`app/models/bot.py`), `advice_data` has `nullable=True` (so it can be `None` in the database). What happens on line 17 of `bot_service.py` (`if str(question_id) in self.bot.advice_data:`) when `self.bot.advice_data` is `None`? And what if `GhostEngine` also needs to check whether the human answered in under 5 seconds (or use a deterministic fallback instead of `random.randint(0, 3)`)?
* **What you learn by fixing it:** Defensive programming with nullable JSON columns (`(self.bot.advice_data or {})`).

---

## Part 5: Completing Miwa in 5 Vertical Slices (Backend + Frontend Together)

Once you have traced the architecture and completed the 6 Forensic Labs above, **do not go back to the old horizontal day-by-day plan**. Finish the project in **5 self-contained Vertical Slices**.

First, enable FastAPI to talk to your browser by adding `CORSMiddleware` (or mounting `/frontend` as `StaticFiles`) in `app/main.py`—otherwise the browser will block your `fetch()` calls due to Cross-Origin Resource Sharing (CORS) rules.

### Slice 1: Identity & Session Loop (Auth View $\leftrightarrow$ `routes/auth.py`)
* **Goal:** Register and log in from `frontend/index.html`, store the `session_id` cookie, and load your own username & ELO from `GET /api/user/me`.
* **What you will wire:**
  1. Fix the HTML IDs in `frontend/index.html` (notice line 38 currently has `id="username-group"` on both the `<div>` and the `<input>`!).
  2. In `frontend/src/app.ts`, write an event listener for `#auth-form` (`submit`).
  3. Call `fetch("http://localhost:8000/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include", body: JSON.stringify({ username, password }) })`.
  4. Immediately call `fetch("http://localhost:8000/api/user/me", { credentials: "include" })` and render the returned `username` and `elo` into the DOM.
* **Core Concept Mastered:** How HTTP cookies (`httponly=True`, `credentials: "include"`), JSON serialization, and `Depends(get_current_player)` work together across browser and server.

### Slice 2: The Lobby, Stats & Leaderboard Loop (`#lobby-view` $\leftrightarrow$ `routes/user.py`)
* **Goal:** Populate the Lobby Dashboard cards (`ELO`, `Matches Played`, `Win Rate`, `Streak`) and Leaderboard table from real PostgreSQL data.
* **What you will wire:**
  1. Build the `#lobby-view` HTML structure in `frontend/index.html` and style it in `frontend/styles.css` (following your `frontend/miwaFrontend.md` guide).
  2. Fetch `GET /api/user/{id}/stats` and `GET /api/leaderboard` and render the rows dynamically using `document.createElement("tr")`.
  3. Add a `GET /api/user/{id}/matches` endpoint (or query recent completed `Match` rows where `player1_id == id` or `player2_id == id`) so the Match History table shows real matches from PostgreSQL instead of hardcoded mock data.
* **Core Concept Mastered:** SQLAlchemy queries (`filter`, `order_by`, `limit`), Pydantic response filtering (`UserStats`, `UserResponse`), and DOM manipulation.

### Slice 3: The Matchmaking & Lobby WebSocket Loop (`routes/matches.py` + `/ws/lobby/{player_id}`)
* **Goal:** Click "Find 1v1 Opponent" in two browser windows, watch the search timer tick, and receive the real-time `match_found` or `bot_offer` WebSocket event.
* **What you will wire:**
  1. When entering the lobby or clicking "Find Opponent", open `new WebSocket("ws://localhost:8000/ws/lobby/" + currentPlayer.id)`.
  2. Call `POST /api/matchmaking/join?category=Math`.
  3. Listen to `lobbySocket.onmessage`:
     * When `event === "match_found"`, read `data.match_id` and switch the view to `#battle-view`.
     * When `event === "bot_offer"`, show a prompt allowing the player to call `GET /api/bots` and `POST /api/matchmaking/switch-to-bot`.
* **Core Concept Mastered:** Why HTTP + WebSockets work as a pair (HTTP `POST` puts you in `app.state.pool`; the background `asyncio` task `run_matchmaking` pairs you 10 seconds later and pushes `match_found` down `app.state.global_manager`).

### Slice 4: The Live 1v1 Quiz Battle Loop (`/ws/match/{match_id}/{player_id}` $\leftrightarrow$ `GameService`)
* **Goal:** Play a complete 10-question match between two browser tabs (or against `GhostEngine`) from `join_match` to `match_ended`.
* **What you will wire:**
  1. Add `<section id="battle-view" class="view-section hidden">` to `frontend/index.html` (header with scores, question text, 4 option buttons, 30s visual countdown, opponent status text).
  2. Connect to `ws://localhost:8000/ws/match/${matchId}/${playerId}` and send `{"event": "join_match"}` inside `ws.onopen`.
  3. Write a clean `switch (msg.event)` state machine in `frontend/src/app.ts` handling the server events:
     * `question_start` $\rightarrow$ render `q_text` and 4 `q_options` buttons, reset 30s timer.
     * Button click $\rightarrow$ send `{"event": "submit_answer", "data": {"answer": index}}`.
     * `player_answered` $\rightarrow$ update opponent status indicator (`"Ataandash joop berdi"`).
     * `question_results` $\rightarrow$ highlight the `correct_answer` button green, update `current_score`.
     * `match_ended` $\rightarrow$ display the final overlay (`status`, `score`, `progress` ELO delta) and a button to return to the Lobby (which refreshes your stats!).
* **Core Concept Mastered:** Event-driven state machines, server-authoritative timers (`_question_timer`), and in-memory vs. persistent state (`GameService._end_match`).

### Slice 5: Practice & Invite Modes + Hardening
* **Goal:** Hook up the Create Invite (`POST /api/matches/create-invite`) and Join Invite (`POST /api/matches/join-invite`) buttons in the Lobby so two friends can enter a 6-character `room_code` and jump straight into Slice 4's `#battle-view`, plus Practice mode (solo/bot play with no ELO change).

---

## Part 6: Self-Test Checkpoints (How You Know You Truly Learned It)

Instead of measuring progress by "lines of code pushed," test yourself with these **5 Architectural Checkpoints**. When you can answer all five without looking at AI or notes, you have genuinely mastered web backend architecture:

1. **The Lifecycle Question:** *"If I restart the `uvicorn` server while two players are waiting in the matchmaking queue and two other players are on Question 5 of a match, what is lost and what survives? Why?"*
   *(Hint: Check what lives in `app.state` vs. what lives in PostgreSQL `matches` and `sessions`.)*
2. **The Dependency Question:** *"If a user calls `POST /api/matchmaking/join` with an expired `session_id` cookie, does the first line of `matchmaking()` in `app/routes/matches.py` ever execute? Which file and line stops it, and does `db.close()` still run?"*
3. **The Concurrency Question:** *"In `GameService.start_question()`, we call `asyncio.create_task(self._question_timer(app))`. Why doesn't `await asyncio.sleep(30)` inside `_question_timer` freeze the entire FastAPI server for 30 seconds for all other players?"*
4. **The ORM Question:** *"In `GameService._end_match()`, we modify `winner.elo = result_elo[0]` and `match.status = MatchStatus.COMPLETED`, and then call `db.commit()` without ever calling `db.add(winner)`. How did SQLAlchemy know to send an `UPDATE` statement for `winner`?"*
   *(Hint: SQLAlchemy's Session keeps an 'Identity Map' that tracks every object loaded from that session and automatically diffs dirty attributes on `commit()`!)*
5. **The Protocol Question:** *"Why did we use HTTP `POST /api/login` for logging in, but a WebSocket `/ws/match/{match_id}/{player_id}` for the quiz battle? What would go wrong if we tried to build the 1v1 battle using only HTTP `GET`/`POST` requests?"*
