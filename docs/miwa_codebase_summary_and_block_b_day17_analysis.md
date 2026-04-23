# Miwa Codebase Summary + Block B Compliance Audit (up to Day 17)

Scope: this review covers only **Block B (Miwa app work)** from `miwa_roadmap_v5.txt`, through **Day 17 inclusive**, and summarizes every tracked file in the current repository state.

## 1) Summary of each tracked file

| File | Summary |
|---|---|
| `.gitignore` | Ignores `venv/`, `__pycache__/`, and `.env`. |
| `app/__init__.py` | Empty package marker. |
| `app/blank.py` | Empty placeholder file. |
| `app/core/__init__.py` | Empty package marker. |
| `app/core/dependencies.py` | Auth dependency: reads `session_id` cookie, validates DB session expiry, returns current `Player`. |
| `app/core/events.py` | Defines WebSocket event constants (`join_match`, `player_joined`, `match_update`, etc.). |
| `app/core/security.py` | Password hashing/verification via Passlib bcrypt wrapper (`Hasher`). |
| `app/database.py` | Loads env vars, builds SQLAlchemy engine/session/base for PostgreSQL, exposes `get_db()`. |
| `app/global_manager.py` | Tracks lobby sockets by player ID and can push `match_found` / `bot_offer` notifications. |
| `app/main.py` | FastAPI app bootstrap; creates tables; initializes shared app state (pool/managers/active_games); starts matchmaking background task; registers routers. |
| `app/models/__init__.py` | Empty package marker. |
| `app/models/bot.py` | `Bot` model with `performance_data` and `advice_data` JSON fields. |
| `app/models/match.py` | Match model + enums for status/mode; stores players, scores, winner, questions/answers JSON, invite code. |
| `app/models/question.py` | Base question abstraction + `MultipleChoice` model with text/options/correct answer/category. |
| `app/models/session.py` | Session table model keyed by `session_token`, includes expiry and optional JSON payload. |
| `app/models/user.py` | Abstract `BaseUser`; concrete `Player` and `Admin` models with auth/stats fields. |
| `app/room_manager.py` | In-memory match-room socket registry; supports connect/disconnect/broadcast/send_to. |
| `app/routes/__init__.py` | Empty package marker. |
| `app/routes/auth.py` | Register/login/me endpoints; sets HTTP-only session cookie on login. |
| `app/routes/matches.py` | Invite match routes, matchmaking join/cancel, bots listing, switch-to-bot match creation, GhostEngine/GameService setup. |
| `app/routes/user.py` | User profile/stat endpoints, leaderboard, self-update, self-delete. |
| `app/routes/ws.py` | WebSocket endpoints for match gameplay and lobby; handles join flow, answer submission, game startup for PvP and bot matches. |
| `app/schemas/__init__.py` | Empty package marker. |
| `app/schemas/match.py` | Pydantic schema for bot switch request (`bot_id`, `category`). |
| `app/schemas/user.py` | Pydantic schemas for register/login/response/stats/update payloads. |
| `app/services/__init__.py` | Empty package marker. |
| `app/services/auth_service.py` | Registration/login business logic, session creation, password checks. |
| `app/services/bot_service.py` | `GhostEngine`: bot response behavior from performance/advice data plus fallback behavior. |
| `app/services/elo_service.py` | ELO rating update calculation utility. |
| `app/services/game_service.py` | Core live match state machine: question start, answer handling, timers, scoring, match completion, DB updates, WS result events. |
| `app/services/match_service.py` | Invite code generator and invite match creation. |
| `app/services/matchmaking_service.py` | `WaitingPlayer` and `MatchmakingPool` queue/mutual-window pairing logic. |
| `app/services/run_mm_service.py` | Background loop: expands windows, creates ranked matches from pool, notifies players, sends bot-offer after wait threshold. |
| `docs/rest_checklist.md` | Manual REST endpoint smoke checklist with expected inputs/outputs marked pass. |
| `miwa_roadmap_v5.txt` | Multi-day learning/dev roadmap defining Block A/B/C/D tasks and notes. |
| `prompt.txt` | Local collaboration rules/notes for assistant behavior during development. |

---

## 2) Block B compliance analysis (Days 10–17, inclusive)

Legend: ✅ Compliant, ⚠️ Partial, ❌ Not compliant (based on current code).

| Day | Block B requirement focus | Status | Notes |
|---|---|---|---|
| 10 | Connection manager with connect/disconnect/broadcast/send_to; WS events constants; basic WS endpoint | ✅ | `app/room_manager.py` implements required methods (all async sends), `app/core/events.py` has 9 constants, WS endpoint exists in `app/routes/ws.py`. |
| 11 | WaitingPlayer + MatchmakingPool + join route + singleton pool + background tick | ✅ | `app/services/matchmaking_service.py`, `app/routes/matches.py`, app lifespan in `app/main.py`, and periodic loop in `app/services/run_mm_service.py` are present. |
| 14 | GameService state tracker, join_match wiring, first question start from pre-selected IDs | ✅ | `app/services/game_service.py` stores per-match state in memory and drives question flow; `ws.py` starts game when players joined; question IDs come from match creation. |
| 15 | submit_answer handling, player_answered broadcast, question resolution | ✅ | Implemented through `WSEvents.SUBMIT_ANSWER` in `ws.py` and `GameService.handle_answer/_resolve_question`. |
| 16 | End match, winner + tie-break, ELO/stats update, answers_data persistence, match_ended broadcast | ✅ | `GameService._determine_result()` + `_end_match()` handles finalization and broadcasts. |
| 17 | GhostEngine deterministic playback from `performance_data`, non-random fallback, advice condition, timeout integration | ⚠️ | GhostEngine exists and is integrated for switch-to-bot flow, but fallback currently uses random timing/answers (not deterministic), advice trigger does not check “human answered under 5s”, and background matchmaking sends bot offer rather than automatically assigning bot. |

### Day 17 specific gap details
- `app/services/bot_service.py` fallback currently uses `random.uniform()` and `random.randint()`; roadmap requires deterministic no-random fallback.
- Advice dispatch in `GhostEngine` is based on advice existence only; roadmap specifies extra condition tied to human fast answer.
- `app/services/run_mm_service.py` offers bot after timeout but does not auto-start bot match from pool timeout path.

---

## 3) Logical runtime analysis (if code is run now)

## Likely to work fine
- FastAPI startup, router registration, and shared app state initialization.
- Password hash/verify path (`Hasher`) and auth flows (register/login/session cookie/me).
- Basic user CRUD/stats/leaderboard endpoints.
- Matchmaking queue mechanics (enqueue/dequeue/mutual ELO window checks/tick expansion).
- Invite match creation and joining.
- WebSocket room connect/disconnect/broadcast/send_to behavior.
- Core PvP game loop: question start, answer capture, timeout completion, scoring, final result broadcasts.

## Might work but with caveats
- Bot match route (`/api/matchmaking/switch-to-bot`) starts a playable ghost game, but data model usage mixes bot ID into `player2_id` instead of dedicated bot field, which can complicate downstream assumptions/analytics.
- Ghost advice sending can fail if `advice_data` is null/absent (membership check on `None` can raise).
- App startup calls `Base.metadata.create_all(bind=engine)` directly; if env vars or DB connectivity are invalid, startup will fail immediately.

## Likely not aligned / may fail expected behavior
- Day 17 deterministic fallback requirement is not met (current ghost fallback is random).
- Timeout-to-bot auto-assignment path is not implemented (only notification offer is sent).
- Advice timing rule (“only if human answered under 5 seconds”) is not enforced.

---

## 4) Hypothetical backend smoke test (no frontend)

Goal: verify MVP backend behavior end-to-end using HTTP client + WebSocket client scripts.

1. **Boot server and DB connectivity**
   - Start app, verify `/health` and `/`.
2. **Auth baseline**
   - Register two users, login both, confirm `session_id` cookies.
3. **User endpoints**
   - `/api/user/me`, `/api/user/{id}`, update own profile, leaderboard fetch.
4. **Invite flow**
   - User A create invite, User B join by code, verify match state in `/api/match/{id}`.
5. **Matchmaking PvP**
   - Both users join same category queue, wait for `match_found` lobby WS events.
6. **PvP gameplay WS**
   - Open two `/ws/match/{match_id}/{player_id}` sockets.
   - Send `join_match`, observe player join notifications and first `question_start`.
   - Send `submit_answer` from both; confirm `player_answered`, then `question_results`.
   - Run through all questions; verify `match_ended` and player stat/ELO changes.
7. **Bot flow**
   - Add/select bot; call `/api/matchmaking/switch-to-bot`; open WS for human.
   - Verify ghost answers are produced and match can complete.
   - Validate current fallback behavior works functionally, even if not roadmap-perfect.
8. **Failure-path smoke**
   - Invalid room code, duplicate queue join, unauthenticated routes, stale session token.

MVP note: for MLP/MVP expectations, current backend is functionally meaningful already for core loops; main shortfall is strict Day 17 ghost behavior compliance, not overall app viability.
