# Miwa Codebase Summary + Block B Compliance (Day 1–11)

## Scope
- Repository: `samarbaike/miwa`
- Scope requested: Miwa project only, Block B only, up to **Day 11 inclusive** from `miwa_roadmap_v5.txt`
- Snapshot: current repository state on this branch

## File-by-file summary

| File | Summary |
|---|---|
| `/.gitignore` | Ignores local Python/env artifacts (`venv/`, `__pycache__/`, `.env`). |
| `/prompt.txt` | High-level guidance note telling the assistant to align instructions with roadmap progress and avoid full copy-paste code. |
| `/miwa_roadmap_v5.txt` | 9-week plan with daily Block A/B/C/D tasks, including Miwa backend milestones and Day 10–11 websocket/matchmaking notes. |
| `/docs/rest_checklist.md` | REST smoke-test checklist table; currently contains only two endpoints and many empty rows. |
| `/app/__init__.py` | Package marker file (empty). |
| `/app/main.py` | FastAPI entrypoint; creates DB tables, mounts routers, initializes lifespan state, and starts a background matchmaking tick loop. |
| `/app/database.py` | Loads DB env vars, builds SQLAlchemy engine/session/base, and defines `get_db()` dependency. |
| `/app/global_manager.py` | Tracks active player websockets globally by `player_id` and can notify a player with `match_found`. |
| `/app/room_manager.py` | Match-room websocket manager keyed by `match_id` and `player_id`; supports connect/disconnect/broadcast/send_to. |
| `/app/core/__init__.py` | Package marker file (empty). |
| `/app/core/security.py` | Password hashing/verification via Passlib bcrypt in `Hasher` utility class. |
| `/app/core/events.py` | `WSEvents` constant container for websocket protocol event names (9 constants). |
| `/app/core/dependencies.py` | `get_current_player` cookie/session auth dependency with expiration and player existence checks. |
| `/app/models/__init__.py` | Package marker file (empty). |
| `/app/models/user.py` | SQLAlchemy user inheritance model: abstract `BaseUser`, concrete `Player` and `Admin`. |
| `/app/models/session.py` | Session table model (`SessionTable`) with token PK, JSON session data, and expiry timestamp. |
| `/app/models/question.py` | Abstract `Question` + concrete `MultipleChoice` question model (body/options/correct/category/image). |
| `/app/models/match.py` | Match enums (`MatchStatus`, `MatchMode`) and `Match` table for players, status/mode, scores, questions/answers, invite code. |
| `/app/models/bot.py` | Ghost bot model with identity/backstory plus JSON performance/advice payloads. |
| `/app/routes/__init__.py` | Package marker file (empty). |
| `/app/routes/auth.py` | Register/login routes, session cookie set on login, and authenticated `/api/user/me` endpoint. |
| `/app/routes/user.py` | User profile/stats/leaderboard routes plus user update/delete with ownership checks. |
| `/app/routes/matches.py` | Invite match creation, match lookup, and matchmaking join endpoint with queue and active-match guards. |
| `/app/routes/ws.py` | WebSocket endpoint at `/ws/match/{match_id}` for room connect + receive-json + broadcast echo behavior. |
| `/app/services/__init__.py` | Package marker file (empty). |
| `/app/services/auth_service.py` | Auth business logic for registration, password verification, and session creation. |
| `/app/services/elo_service.py` | ELO formula utility returning new ratings for winner and loser. |
| `/app/services/match_service.py` | Invite-room code generation and invite match persistence. |
| `/app/services/matchmaking_service.py` | `WaitingPlayer` + `MatchmakingPool` queue logic (`enqueue/dequeue/try_pair/tick`) plus module-global pool instance `miwa_pool`. |
| `/app/schemas/__init__.py` | Package marker file (empty). |
| `/app/schemas/user.py` | Pydantic request/response schemas for register/login/user response/stats/user update. |

## Block B compliance analysis (Day 1–11 only)

### Day 1 (Block B): project scaffold + health endpoint
- **Status:** ✅ Mostly compliant
- **Evidence:** `app/main.py` includes FastAPI app with `/` and `/health`; package structure exists.

### Day 2 (Block B): models (user/question/match/bot)
- **Status:** ✅ Compliant
- **Evidence:** `app/models/user.py`, `question.py`, `match.py`, `bot.py` are present with required classes/enums.

### Day 3 (Block B): schemas + security + auth register + session model
- **Status:** ✅ Compliant
- **Evidence:** `app/schemas/user.py`, `app/core/security.py`, `app/services/auth_service.py`, `app/models/session.py`.

### Day 7 (Block B): auth routes + session cookie + current user dependency
- **Status:** ✅ Compliant
- **Evidence:** `app/routes/auth.py` implements register/login and cookie set; `app/core/dependencies.py` implements current player lookup.

### Day 8 (Block B): ELO service + user routes
- **Status:** ✅ Compliant
- **Evidence:** `app/services/elo_service.py`; `app/routes/user.py` contains profile/stats/leaderboard routes.

### Day 9 (Block B): match routes + REST checklist completion
- **Status:** ⚠️ Partially compliant
- **Evidence (done):** `app/routes/matches.py` includes invite creation and match lookup routes.  
- **Gap:** `docs/rest_checklist.md` is not complete for “every endpoint built so far”; mostly blank placeholders remain.

### Day 10 (Block B): websocket manager + events + ws echo route
- **Status:** ⚠️ Partially compliant
- **Evidence (done):**
  - Event constants exist in `app/core/events.py` (all 9 named constants present).
  - Echo-style websocket route exists in `app/routes/ws.py`.
- **Gaps:**
  - `app/routes/ws.py` imports `app.websocket_manager` (`manager`), but that file is not present in repository.
  - Manager implementation exists as `RoomManager` in `app/room_manager.py`, indicating naming/wiring inconsistency.

### Day 11 (Block B): matchmaking service + join route + background tick + singleton wiring
- **Status:** ⚠️ Partially compliant
- **Evidence (done):**
  - `WaitingPlayer`/`MatchmakingPool` and required methods exist in `app/services/matchmaking_service.py`.
  - `/api/matchmaking/join` route exists (in `app/routes/matches.py`).
  - Background tick task exists in `app/main.py` via `asyncio.create_task(run_matchmaking(...))`.
  - Enum mismatch note appears already addressed in active-match guard (`MatchStatus.IN_PROGRESS`) and invite creation (`MatchStatus.WAITING`).
- **Gap (important):**
  - Day 11 singleton rule is not fully followed: `main.py` initializes `app.state.pool`, but route logic uses module-global `miwa_pool` from service file, so it is not guaranteed to use the same app-lifetime shared instance.
  - Day 11 note also expected connection manager singleton on app state; current websocket path still references missing `app.websocket_manager`.

## Overall Day 1–11 Block B verdict
- **Implemented foundation:** strong for core models, auth, schemas, ELO, basic matchmaking concepts.
- **Main blockers before later websocket/game-loop days:**  
  1. Unify websocket manager wiring (remove missing import mismatch).  
  2. Enforce app-lifespan singleton usage for matchmaking pool (and websocket manager) through `app.state`.  
  3. Complete REST checklist coverage to match built endpoints.
