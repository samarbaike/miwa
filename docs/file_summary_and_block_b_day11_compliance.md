# Miwa Repository File Summary + Block B Compliance (through Day 11)

## Scope
- Repository: `samarbaike/miwa`
- Analysis source plan: `/home/runner/work/miwa/miwa/miwa_roadmap_v3.txt`
- Roadmap scope applied: **Block B only**, **through Day 11 (inclusive)**
- File inventory basis: tracked files from latest repository commit

## File-by-file summary

### Root files
- `.gitignore`: ignores `venv/`, `__pycache__/`, and `.env`.
- `.miwa_roadmap_v3.txt.swp`: Vim swap file currently tracked in git.
- `miwa_roadmap_v3.txt`: roadmap with day-by-day plan and Block A/B/C/D tasks.
- `prompt.txt`: guidance note for assistants on how to support development flow.

### Docs
- `docs/rest_checklist.md`: REST smoke-test table with only two currently listed endpoints (`create-invite`, `get match by id`), leaving many rows empty.

### App package markers
- `app/__init__.py`: empty package marker.
- `app/core/__init__.py`: empty package marker.
- `app/models/__init__.py`: empty package marker.
- `app/routes/__init__.py`: empty package marker.
- `app/schemas/__init__.py`: empty package marker.
- `app/services/__init__.py`: empty package marker.

### App bootstrap and infrastructure
- `app/main.py`: FastAPI app entrypoint; creates DB tables on startup, mounts routers, starts background matchmaking loop (`tick()` every 10s), and exposes `/` + `/health` endpoints.
- `app/database.py`: SQLAlchemy engine/session setup via environment variables (`user`, `password`, `host`, `port`, `dbname`), with `get_db()` dependency generator.
- `app/websocket_manager.py`: in-memory `ConnectionManager` keyed by `match_id`; supports `connect`, `disconnect`, and `broadcast`.

### Core
- `app/core/security.py`: password hash/verify helpers using Passlib bcrypt context.
- `app/core/dependencies.py`: `get_current_player` dependency using `session_id` cookie and `sessions` table expiry checks.
- `app/core/events.py`: WebSocket event constants class (`WSEvents`) with six event names.

### Models
- `app/models/user.py`: abstract `BaseUser` and concrete `Player`/`Admin` SQLAlchemy models.
- `app/models/session.py`: `SessionTable` model for cookie sessions with expiry and JSON session payload.
- `app/models/match.py`: `Match` model plus `MatchStatus` and `MatchMode` enums; stores participants, scores, invite code, and JSON payload fields.
- `app/models/question.py`: abstract `Question` and concrete `MultipleChoice` model; includes commented-out `ColumnBased` draft.
- `app/models/bot.py`: `Bot` model with deterministic `performance_data` and optional `advice_data` JSON fields.

### Schemas
- `app/schemas/user.py`: Pydantic request/response schemas (`UserRegister`, `LoginRequest`, `UserResponse`, `UserStats`).

### Services
- `app/services/auth_service.py`: registration and login logic; hashes passwords and creates session rows.
- `app/services/elo_service.py`: Elo rating calculator for winner/loser pair.
- `app/services/match_service.py`: invite-room code generation and invite match creation.
- `app/services/matchmaking_service.py`: `WaitingPlayer` + `MatchmakingPool` queue with ELO window expansion, enqueue/dequeue, and pairing logic.

### Routes
- `app/routes/auth.py`: register/login endpoints and protected `/api/user/me` endpoint.
- `app/routes/user.py`: user profile, user stats, and leaderboard endpoints.
- `app/routes/matches.py`: invite creation, match lookup, and matchmaking join endpoint.
- `app/routes/ws.py`: WebSocket endpoint that echoes JSON messages to all sockets in a match room.

---

## Block B compliance analysis (Day 7 to Day 11)

### Day 7 (Block B)
Planned:
- `POST /api/register`, `POST /api/login` as thin handlers calling `AuthService`
- cookie-based session creation
- `get_current_player` dependency

Status: **Mostly compliant**
- Implemented in `app/routes/auth.py`, `app/services/auth_service.py`, `app/core/dependencies.py`.
- Routes are thin and delegate to service.
- Cookie session flow exists.

Notes:
- `register` checks existing email only (not username conflict), but this is not explicitly required by Day 7 text.

### Day 8 (Block B)
Planned:
- `EloService.calculate_new_ratings`
- user profile/stats/leaderboard routes

Status: **Compliant**
- Elo service exists in `app/services/elo_service.py` with expected formula structure.
- `GET /api/user/{id}`, `GET /api/user/{id}/stats`, `GET /api/leaderboard` exist in `app/routes/user.py`.

### Day 9 (Block B)
Planned:
- `GET /api/match/:id`
- `POST /api/matches/create-invite`
- complete `docs/rest_checklist.md` for all built endpoints

Status: **Partially compliant**
- Match and invite endpoints implemented in `app/routes/matches.py`.
- `docs/rest_checklist.md` is **not complete** (only two rows populated; expected “every endpoint built so far”).

Potential implementation mismatch:
- `MatchService.create_invite_match` currently sets `status="WAITING"` (uppercase string), while the declared enum values are lowercase (`waiting`, `in_progress`, `completed`), so this is a likely mismatch.
- `Match` model requires `mode` non-null, but invite creation does not set it.

### Day 10 (Block B)
Planned:
- `ConnectionManager` with `connect`, `disconnect`, `broadcast`, `send_to`
- `WSEvents` class with **9** event names (8 spec + `match_found`)
- `/ws/match/{match_id}` echo endpoint

Status: **Partially compliant**
- WebSocket echo endpoint exists and works conceptually (`app/routes/ws.py`).
- `ConnectionManager` exists but **missing `send_to`** (`app/websocket_manager.py`).
- `WSEvents` exists but has **6 constants**, not planned 9 (`app/core/events.py`).

### Day 11 (Block B)
Planned:
- `WaitingPlayer` + `MatchmakingPool` with enqueue/dequeue/try_pair/tick
- `POST /api/matchmaking/join`
- background task that runs `pool.tick()` every 10 seconds on app start

Status: **Mostly compliant**
- Service classes/methods implemented in `app/services/matchmaking_service.py`.
- Join endpoint implemented in `app/routes/matches.py` (different filename than plan text, but functional placement is acceptable).
- Background tick task implemented in `app/main.py` via `asyncio.create_task(run_matchmaking())` and `await asyncio.sleep(10)`.

Potential logic mismatch:
- “already in active match” guard checks `Match.status == "active"`, but `"active"` is not one of the declared enum values (`waiting`, `in_progress`, `completed`; likely intended runtime value is `in_progress`). This may fail to enforce intended guard.

---

## Overall compliance verdict (Block B, Day 7-11)
- **Implemented and present:** core auth/session flow, Elo service, user routes, invite/match routes, WebSocket echo baseline, matchmaking pool, join endpoint, and startup matchmaking tick.
- **Main gaps against roadmap by Day 11:**
  1. `docs/rest_checklist.md` not complete (Day 9 deliverable shortfall).
  2. `ConnectionManager.send_to` missing (Day 10 shortfall).
  3. `WSEvents` constants incomplete vs planned 9 events (Day 10 shortfall).
  4. Some status/mode consistency issues in match creation/active-match checks (affects Day 9/11 runtime correctness).

Net result: **partially compliant overall**, with strong foundational completion but several explicit Day 9-11 deliverable gaps.
