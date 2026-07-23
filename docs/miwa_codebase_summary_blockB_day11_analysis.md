# Miwa Codebase File Summary + Block B Compliance (Day 1–Day 11)

## Scope
- Source of truth: `/home/runner/work/miwa/miwa/miwa_roadmap_v5.txt`
- Compliance window: **Block B only, Day 1 through Day 11 (inclusive)**
- Repository-only interpretation: non-Miwa coursework entries are marked **Out of scope for this repo**

---

## File-by-file summary

### Repository root

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/.gitignore` | Ignores local environment and cache artifacts (`venv/`, `__pycache__/`, `.env`). |
| `/home/runner/work/miwa/miwa/miwa_roadmap_v5.txt` | Master day-by-day roadmap; includes expected Miwa milestones and audit notes (e.g., Day 10/11 websocket + matchmaking constraints). |
| `/home/runner/work/miwa/miwa/prompt.txt` | Internal instruction text describing how to use the roadmap and constraints for guidance. |

### Documentation

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/docs/rest_checklist.md` | Smoke-test checklist for implemented REST endpoints and expected responses; marked pass for listed routes. |

### App package

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/app/__init__.py` | Package marker file (no runtime logic). |
| `/home/runner/work/miwa/miwa/app/main.py` | FastAPI entrypoint; creates DB tables, initializes shared managers/pool in lifespan, starts background matchmaking task, and mounts routers. |
| `/home/runner/work/miwa/miwa/app/database.py` | SQLAlchemy engine/session/base setup from `.env` variables; exports `get_db()` dependency generator. |
| `/home/runner/work/miwa/miwa/app/global_manager.py` | Global lobby websocket manager keyed by player ID; supports connect/disconnect and match-found notification. |
| `/home/runner/work/miwa/miwa/app/room_manager.py` | Match-room websocket connection manager keyed by `match_id` and `player_id`; supports connect/disconnect/broadcast/send_to. |

### Core

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/app/core/__init__.py` | Package marker file (no runtime logic). |
| `/home/runner/work/miwa/miwa/app/core/security.py` | Password hashing and verification wrapper (`Hasher`) using Passlib bcrypt context. |
| `/home/runner/work/miwa/miwa/app/core/dependencies.py` | Auth dependency `get_current_player`; reads `session_id` cookie, validates session expiry, returns authenticated player. |
| `/home/runner/work/miwa/miwa/app/core/events.py` | Central websocket event constant class `WSEvents` with 9 event names including `match_found`. |

### Models

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/app/models/__init__.py` | Package marker file (no runtime logic). |
| `/home/runner/work/miwa/miwa/app/models/user.py` | User hierarchy model definitions: abstract `BaseUser`, concrete `Player`, and `Admin`. |
| `/home/runner/work/miwa/miwa/app/models/session.py` | Session persistence model storing session token, player binding, JSON session data, and expiration. |
| `/home/runner/work/miwa/miwa/app/models/match.py` | Match enums (`MatchStatus`, `MatchMode`) plus `Match` table for players, status/mode, scores, JSON payloads, and invite code. |
| `/home/runner/work/miwa/miwa/app/models/question.py` | Abstract question base + concrete `MultipleChoice` question model; includes category/options/correct answer fields. |
| `/home/runner/work/miwa/miwa/app/models/bot.py` | Bot model with deterministic performance/advice JSON payload storage. |

### Schemas

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/app/schemas/__init__.py` | Package marker file (no runtime logic). |
| `/home/runner/work/miwa/miwa/app/schemas/user.py` | Pydantic schemas for registration, login, user response, user stats, and partial user update. |

### Services

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/app/services/__init__.py` | Package marker file (no runtime logic). |
| `/home/runner/work/miwa/miwa/app/services/auth_service.py` | Authentication service implementing register/login, password verification, and session token creation. |
| `/home/runner/work/miwa/miwa/app/services/elo_service.py` | Elo rating update calculation for winner/loser using standard expected-score formula and K=32. |
| `/home/runner/work/miwa/miwa/app/services/match_service.py` | Invite match service creating 6-char room codes and inserting WAITING invite matches. |
| `/home/runner/work/miwa/miwa/app/services/matchmaking_service.py` | Matchmaking domain with `WaitingPlayer` and queue-backed `MatchmakingPool` (`enqueue`, `dequeue`, `try_pair`, `tick`). |
| `/home/runner/work/miwa/miwa/app/services/run_mm_service.py` | Long-running async matchmaking loop: ticks windows, pairs players, writes ranked matches, sends `match_found` notifications every cycle. |

### Routes

| File | Summary |
|---|---|
| `/home/runner/work/miwa/miwa/app/routes/__init__.py` | Package marker file (no runtime logic). |
| `/home/runner/work/miwa/miwa/app/routes/auth.py` | REST auth endpoints: register/login and `/api/user/me` via session-cookie dependency. |
| `/home/runner/work/miwa/miwa/app/routes/user.py` | User profile/stats/leaderboard CRUD-related endpoints with auth checks on update/delete. |
| `/home/runner/work/miwa/miwa/app/routes/matches.py` | Match endpoints for invite creation/joining, match fetch, and matchmaking join/cancel queue actions. |
| `/home/runner/work/miwa/miwa/app/routes/ws.py` | WebSocket endpoints for per-match room communication and per-player lobby channel registration. |

---

## Block B compliance analysis (Day 1–Day 11)

### Legend
- **Compliant**: implemented and aligned with roadmap intent
- **Partially compliant**: implemented but with naming/path/structure drift from roadmap
- **Out of scope for this repo**: roadmap item is non-Miwa coursework content

| Day | Block B target in roadmap | Current repo status | Compliance |
|---|---|---|---|
| Day 1 | Miwa scaffold + folder structure + health/root endpoints | Present (`app/main.py`, package structure, root + health). | **Compliant** |
| Day 2 | DB setup + core models (user/question/match/bot) | Present (`app/database.py`, all listed models). | **Compliant** |
| Day 3 | User schemas + security + auth register + session model | Present (`app/schemas/user.py`, `app/core/security.py`, `app/services/auth_service.py`, `app/models/session.py`). | **Compliant** |
| Day 4 | (Roadmap row shows Applied Stats notebook) | No notebook content in this repo (Miwa codebase only). | **Out of scope for this repo** |
| Day 5 | Free day | N/A | **Out of scope for this repo** |
| Day 6 | Free day | N/A | **Out of scope for this repo** |
| Day 7 | Auth routes + login session cookie + `get_current_player` dependency | Present in `app/routes/auth.py` + `app/core/dependencies.py`. | **Compliant** |
| Day 8 | Elo service + user routes (profile/stats/leaderboard) | Present (`app/services/elo_service.py`, `app/routes/user.py`). | **Compliant** |
| Day 9 | Match fetch + invite creation + REST checklist | Present (`app/routes/matches.py`, `app/services/match_service.py`, `docs/rest_checklist.md`). | **Compliant** |
| Day 10 | ConnectionManager (+ send_to), websocket events (9), `/ws/match/{match_id}` echo | Functionality exists but naming/path differs: manager is `RoomManager` (`app/room_manager.py`) and WS route is `/ws/match/{match_id}/{player_id}`; events class has all 9 constants. | **Partially compliant** |
| Day 11 | Matchmaking classes + join route guard + singleton pool + background tick | Present (`app/services/matchmaking_service.py`, join route in `app/routes/matches.py`, singleton `app.state.pool`, task in lifespan). Enum mismatch note appears already addressed. Route file name differs from plan (`matches.py` vs expected `matchmaking.py`). | **Partially compliant** |

---

## Day 11-specific audit notes (from roadmap notes) vs current code

1. **WSEvents constant count requirement (9 total):**
   - Current `app/core/events.py` contains all 9 required constants.
   - Status: **Resolved**.

2. **ConnectionManager `send_to` requirement:**
   - `app/room_manager.py` has async `send_to(match_id, player_id, message)`.
   - Status: **Resolved** (under different class/module name).

3. **Enum mismatch warning (`active` vs `in_progress`, uppercase `WAITING` concern):**
   - Active-match guard uses `MatchStatus.IN_PROGRESS`.
   - Invite creation uses `MatchStatus.WAITING` enum member (whose value is lowercase `"waiting"`).
   - Status: **Resolved in current code**.

4. **Singleton requirement for shared runtime managers on `app.state`:**
   - `MatchmakingPool`, `RoomManager`, and `GlobalManager` are initialized once in lifespan and shared via `app.state`.
   - Status: **Implemented**.

---

## Overall Block B (Day 1–11) conclusion

- **Core delivery is largely on track through Day 11 for Miwa backend functionality.**
- Most milestone capabilities exist and are wired into runtime startup.
- Remaining deviations are mostly **structure/naming drift** from roadmap wording (not major functional gaps), especially around:
  - `ConnectionManager` naming/file placement,
  - websocket route shape,
  - separate `matchmaking.py` route file vs current combined `matches.py` approach.
