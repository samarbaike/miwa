# Miwa — Product & Technical Requirements Specification

> **Project:** Miwa (Real-Time 1v1 ОРТ Quiz Platform)  
> **Target Scale:** Production-ready for up to **5,000 concurrent users** (~2,500 simultaneous live matches / lobby connections)  
> **Stack:** FastAPI, WebSockets, SQLAlchemy + PostgreSQL (Supabase), **React.js** (Vite + React Router + CSS Modules / Standard CSS)  

---

## 1. Product Overview

**Miwa** is a real-time multiplayer educational quiz platform designed for students in Kyrgyzstan preparing for the **ОРТ** (National Standardized University Admission Test). Players compete head-to-head in 10-question battles across three core categories:
1. **Math** — Standard ОРТ mathematics problem-solving.
2. **Grammar** — ОРТ grammar and sentence completion.
3. **Vocabulary (Kyrgyz)** — Word-meaning and meaning-to-word battles designed to build vocabulary needed for analogy sections.

---

## 2. Core Features

| Feature Domain | Description | Current CB(codebase) Modules |
| :--- | :--- | :--- |
| **Authentication & Sessions** | Bcrypt password hashing and stateful HTTP-only cookie sessions (`session_id`) with 24-hour expiration. | `app/routes/auth.py`, `app/services/auth_service.py`, `app/core/security.py`, `app/models/session.py` |
| **Player Profiles & Stats** | Tracks ELO rating (default `110` / configurable), wins, current win streak, total matches played, and Top 20 ELO leaderboard. | `app/routes/user.py`, `app/models/user.py`, `app/schemas/user.py` |
| **Dynamic ELO Matchmaking** | In-memory queue (`MatchmakingPool`) pairing players in the same category. Starts with a `±15` ELO window and expands by `+5` on every background tick. | `app/services/matchmaking_service.py`, `app/services/run_mm_service.py`, `app/global_manager.py` |
| **Live 1v1 WebSocket Battles** | Stateful room-based game loop (`GameService`): 10 random multiple-choice questions, server-authoritative 30-second timer per question, live opponent status, speed tie-breaker, and ELO updates (`EloService`, $K=32$). | `app/routes/ws.py`, `app/services/game_service.py`, `app/services/elo_service.py`, `app/room_manager.py` |
| **GhostEngine (Bot Matches)** | After 60 seconds in queue without a human match, sends a `bot_offer`. Replays recorded human timings/answers (`performance_data`) and sends question hints (`advice_data`) without affecting ELO. | `app/services/bot_service.py`, `app/models/bot.py`, `app/routes/matches.py` |
| **Match Modes** | Supports **Ranked** (1v1 ELO queue), **Invite** (private 6-character `room_code`), and **Practice** (unranked solo/bot play). | `app/models/match.py`, `app/services/match_service.py`, `app/routes/matches.py` |

---

## 3. User Capabilities (What a Basic User Can Do)

### 3.1 Identity & Account Management
- **Register (`POST /api/register`):** Create an account with a unique username (5–50 chars), valid email, and password (8+ chars).
- **Log In (`POST /api/login`):** Authenticate and receive an `HttpOnly` `session_id` cookie.
- **Log Out (`POST /api/logout`):** *(Minor addition)* Invalidate the current session row in `sessions` and clear the cookie.
- **View & Edit Profile (`GET /api/user/me`, `PUT /api/user/{id}`):** View own profile/stats and update username.
- **Delete Account (`DELETE /api/user/{id}`):** Permanently delete own player profile and active sessions.

### 3.2 Lobby & Discovery
- **View Personal Dashboard (`GET /api/user/{id}/stats`):** See current ELO, total matches, win count, win rate percentage, and active streak.
- **View Leaderboard (`GET /api/leaderboard`):** Browse the Top 20 players ordered by ELO.
- **View Match History (`GET /api/user/{id}/matches`):** *(Minor addition)* View recent completed matches (date, opponent, category, score, win/loss/draw, ELO delta).

### 3.3 Matchmaking & Room Creation
- **Join Ranked Queue (`POST /api/matchmaking/join?category=...`):** Enter the matchmaking queue for a chosen category while listening on `/ws/lobby/{player_id}` for `match_found`.
- **Cancel Queue (`POST /api/matchmaking/cancel`):** Leave the matchmaking queue before a match starts.
- **Switch to Bot (`GET /api/bots`, `POST /api/matchmaking/switch-to-bot`):** Upon receiving a `bot_offer` event after 60s of waiting (or immediately in Practice mode), view available bots and start a Ghost match.
- **Create & Join Private Invite Match (`POST /api/matches/create-invite`, `POST /api/matches/join-invite`):** Generate a 6-character alphanumeric room code to share with a friend, or enter a friend's code to start a 1v1 match directly.

### 3.4 Live Quiz Gameplay
- **Connect to Battle Room (`/ws/match/{match_id}/{player_id}`):** Send `join_match` to synchronize readiness.
- **Answer Questions (`submit_answer`):** Read the question prompt (and optional image) and pick one of 4 options within the 30-second server countdown.
- **Observe Opponent Activity (`player_answered`):** See in real time when the opponent has locked in an answer (without revealing which option they chose).
- **Receive Round Feedback & Bot Advice (`question_results`):** See the correct option, updated score, whether the opponent answered, and any educational hint (`advice`) if playing against a Ghost bot.
- **Review Match Outcome (`match_ended`):** View final win/lose/draw result (ties broken by total time spent on correct answers), final score, and new ELO / ELO delta.

---

## 4. Required Application Pages & React.js Architecture

The frontend (`frontend/`) will be built as a **React.js Single-Page Application (SPA)** (bootstrapped with Vite and `react-router-dom`), converting the current HTML sections in `frontend/index.html` into modular React pages, reusable components, and custom hooks:

### 4.1 React Pages & Routes

1. **Home / Landing Page (`/` — `<HomePage />`)**
   - Persistent `<Navbar />` (`Home`, `Lobby`, `Leaderboard`, `Profile`, `Login / Register`).
   - Hero section (`<Hero />`) with value proposition and primary CTAs (`Play 1v1 Now`, `Create Account`).
2. **Authentication Page (`/auth` — `<AuthPage />`)**
   - Controlled `<AuthForm />` component using `useState` to toggle between **Sign In** and **Create Account** modes (`username`, `email` [register only], `password`).
   - Form validation, loading state, error banner, and automatic redirect to `/lobby` upon successful authentication.
3. **Lobby / Dashboard Page (`/lobby` — `<LobbyPage />`, Protected Route)**
   - **Stats Cards Grid (`<StatsGrid />`):** Displays Current ELO + Division badge, Matches Played, Win Rate %, and Current Streak fetched from `GET /api/user/{id}/stats`.
   - **Arena Action Panel (`<MatchmakingPanel />`):**
     - Mode selector tabs: `Ranked 1v1`, `Invite Friend`, `Practice / Bot`.
     - Category selector: `Math`, `Grammar`, `Vocabulary`.
     - Live queue status bar with `useEffect` elapsed timer, `Cancel` button, and **Bot Offer Modal (`<BotOfferModal />`)** triggered on the `bot_offer` WebSocket event (fetches `/api/bots` and calls `/api/matchmaking/switch-to-bot`).
     - Invite controls: `Create Room Code` display and `Join by Code` controlled input.
   - **Recent Matches Table (`<MatchHistoryTable />`):** Renders match rows (`Date`, `Opponent`, `Category`, `Score`, `Result`, `ELO Change`).
4. **Live Battle Arena Page (`/battle/:matchId` — `<BattlePage />`, Protected Route)**
   - **Match Header (`<BattleHeader />`):** Player 1 (Name + Score) vs. Player 2 / Bot (Name + Score), Question counter (`1 / 10`), and reactive 30-second countdown bar.
   - **Question Card (`<QuestionCard />`):** Renders `q_text`, optional diagram/image, and 4 option buttons (`q_options`) with locked/correct/incorrect visual states.
   - **Status & Advice Strip (`<OpponentStatus />` & `<BotAdviceBanner />`):** Real-time indicator when `player_answered` fires, plus Ghost bot hints (`advice`) when present.
   - **End-of-Match Overlay (`<MatchResultModal />`):** Displays Victory/Defeat/Draw banner, final score breakdown, ELO rating delta (`+16` / `-14`), and `Return to Lobby` button.
5. **Leaderboard & Profile Pages (`/leaderboard` — `<LeaderboardPage />`, `/profile` — `<ProfilePage />`)**
   - Top 20 players table (`Rank`, `Username`, `ELO`, `Wins`, `Total Matches`).
   - Account settings form (`Update Username`, `Logout`, `Delete Account` confirmation modal).

### 4.2 Core React State & Custom Hooks
- **`AuthContext` (`useAuth`):** Holds `currentUser` state, verifies session on app load via `GET /api/user/me` (`credentials: "include"`), and provides `login()`, `register()`, and `logout()` actions.
- **`useLobbySocket(playerId)`:** Manages `/ws/lobby/{player_id}` lifecycle inside `useEffect`, handling `match_found` (navigates to `/battle/:matchId`) and `bot_offer` events, and cleans up the socket on unmount.
- **`useBattleSocket(matchId, playerId)`:** Manages `/ws/match/{match_id}/{player_id}`, dispatches `join_match` and `submit_answer`, and updates React state on `question_start`, `player_answered`, `question_results`, and `match_ended`.

---

## 5. Architecture & Codebase Changes for 5,000 Concurrent Users

To stably support **5,000 concurrent users** (e.g., 3,000 users in 1,500 active WebSocket battles + 2,000 users browsing/queuing in the lobby), the following targeted adjustments to the current codebase are required:

### 5.1 Database & Async Event Loop Stability (Critical)
1. **Replace `NullPool` with Connection Pooling (`app/database.py`):**
   - *Current state:* `create_engine(..., poolclass=NullPool)` opens a brand-new TCP + SSL handshake to Supabase on every HTTP request and WebSocket event. Under 5,000 users, PostgreSQL will immediately exhaust `max_connections`.
   - *Required change:* Remove `NullPool` and configure `QueuePool` (`pool_size=20, max_overflow=30, pool_pre_ping=True`) connected to Supabase's **PgBouncer Transaction Pooler** (port `6543`).
2. **Prevent Blocking the Asyncio Event Loop (`app/services/game_service.py`, `app/routes/ws.py`, `app/services/run_mm_service.py`):**
   - *Current state:* Synchronous SQLAlchemy queries (`with Session(engine) as db:`) are executed directly inside `async def` functions (`websocket_endpoint`, `run_matchmaking`, `GameService.__init__`, `GameService._end_match`). Every 50ms DB round-trip freezes the entire event loop for all 5,000 connected WebSockets.
   - *Required change:* Offload synchronous DB blocks using `await asyncio.to_thread(...)` or migrate to SQLAlchemy `AsyncEngine` + `AsyncSession` (`asyncpg`).
3. **Password Hashing Thread Offloading (`app/services/auth_service.py`):**
   - *Current state:* `bcrypt` takes ~100–250ms of CPU time per login/register.
   - *Required change:* Keep `auth.py` routes as standard `def` (so FastAPI runs them in an external threadpool) and ensure `bcrypt` work factor is set to `10` or `12`.

### 5.2 Matchmaking & Game Loop Fixes (Minor Code Changes)
1. **Fix Matchmaking Head-of-Line Blocking (`app/services/matchmaking_service.py`):**
   - *Current state:* `try_pair()` only checks `self.q[0]` against the rest of the queue. If `self.q[0]` has no match in their category/ELO, nobody behind them is ever paired.
   - *Required change:* Partition queues by `category` (`dict[str, list[WaitingPlayer]]`), sort by ELO on each tick, and sweep adjacent pairs in $O(N \log N)$ time. Reduce tick sleep in `run_mm_service.py` from `10s` to `2s`.
2. **Fix Self-Cancelling Question Timer (`app/services/game_service.py`):**
   - *Current state:* When a question times out, `_question_timer` calls `handle_answer` $\rightarrow$ `_resolve_question` $\rightarrow$ `start_question`, which calls `self.question_timer_task.cancel()`—cancelling the very task currently executing.
   - *Required change:* Clear `self.question_timer_task = None` inside `_question_timer` before calling `handle_answer`.
3. **Handle WebSocket Disconnects & Abandoned Matches (`app/routes/ws.py`, `app/services/game_service.py`):**
   - *Current state:* If a player closes their tab mid-match, `room_manager.disconnect()` removes the socket, but `GameService` stays in `app.state.active_games` and `Match.status` stays `IN_PROGRESS` in PostgreSQL forever (permanently blocking the player from queuing again via the 2nd guard in `matches.py`).
   - *Required change:* On disconnect, trigger a 15-second reconnect grace timer; if the player does not reconnect, forfeit the match, award the win to the remaining player, update DB status to `COMPLETED`, cancel `question_timer_task`, and delete `active_games[match_id]`.
4. **Fix Bot Match ID Collision & Nullable Advice (`app/routes/matches.py`, `app/services/game_service.py`, `app/services/bot_service.py`):**
   - *Current state:* `switch_to_bot` stores `bot.id` in `Match.player2_id` instead of `Match.player2_bot_id`, causing issues if `bot.id == player1.id` and querying `Player` with `bot.id` in `_end_match`. Also `bot.advice_data` can be `None`, raising `TypeError` in `GhostEngine`.
   - *Required change:* Save `player2_bot_id=bot.id`, use a negative sentinel ID (`-bot.id`) for the bot inside `GameService`, and guard `if self.bot.advice_data and str(question_id) in self.bot.advice_data:`.
5. **Populate Questions for Invite Matches (`app/services/match_service.py`, `app/routes/matches.py`):**
   - *Current state:* `create_invite_match` leaves `questions_data` as `None`, crashing `GameService` when players join the WebSocket.
   - *Required change:* Accept a `category` parameter in `/api/matches/create-invite`, select 10 random question IDs, and notify Player 1 via WebSocket when Player 2 joins `/api/matches/join-invite`.

### 5.3 Security, CORS & API Hardening
1. **Enable CORS for React Frontend (`app/main.py`):** Add FastAPI `CORSMiddleware` with `allow_origins=["http://localhost:5173", "<production-frontend-domain>"]` and `allow_credentials=True` so the React app can send and receive the `HttpOnly` `session_id` cookie across requests (`fetch(..., { credentials: "include" })`).
2. **Leaderboard Data Leak (`app/routes/user.py`):** Add `response_model=list[UserResponse]` (or a dedicated `LeaderboardEntry` schema without `email`) to `GET /api/leaderboard` so `password_hash` is never serialized.
3. **WebSocket Cookie Authentication (`app/routes/ws.py`):** Validate `websocket.cookies.get("session_id")` when accepting `/ws/lobby` and `/ws/match` connections so users cannot spoof another `player_id` in the URL.
4. **Duplicate Username Check (`app/services/auth_service.py`):** Check `(Player.email == user_in.email) | (Player.username == user_in.username)` before `session.commit()` to return `400 Bad Request` instead of an unhandled `500 IntegrityError`.
5. **Authorization Status Codes (`app/routes/user.py`):** Return `403 Forbidden` instead of `404 Not Found` when `current_user.id != user_id` in `PUT`/`DELETE /api/user/{user_id}`, and set `default=None` on `UserUpdate.username`.

---

## 6. Testing & Verification Plan

### 6.1 Functional Test Suite (Backend `pytest` + React Component/E2E Tests)

| Test Area | Test Cases to Verify | Expected Outcome |
| :--- | :--- | :--- |
| **Auth & Sessions** | 1. Register valid user<br>2. Register duplicate email or username<br>3. Login with valid/invalid credentials<br>4. Access `/api/user/me` with valid, expired, or missing `session_id` cookie | `200 OK` with `UserResponse` (no `password_hash`); `400` on duplicates; `401` on invalid/expired session. |
| **User & Leaderboard** | 1. Fetch `/api/user/{id}/stats` and `/api/leaderboard`<br>2. Update own username (`PUT /api/user/{id}`)<br>3. Attempt to update/delete another user's ID | `200 OK` with filtered schema fields; `403 Forbidden` on cross-user modification. |
| **Matchmaking Pool** | 1. Enqueue 2 players in same category within ELO window<br>2. Enqueue 3 players where index `0` is `"Math"` and indices `1, 2` are `"Grammar"`<br>3. Double-enqueue guard & already-in-match guard<br>4. Cancel queue (`POST /api/matchmaking/cancel`) | Compatible players pair on next tick; head-of-line player does not block others; guards return `400`. |
| **1v1 WebSocket Battle** | 1. Both players connect & send `join_match`<br>2. Both submit answers across 10 questions<br>3. Tie-break scenario (equal scores, different answer times)<br>4. Question timeout (neither or one player answers within 30s)<br>5. Mid-match disconnect / tab close | `question_start` $\rightarrow$ `player_answered` $\rightarrow$ `question_results` $\rightarrow$ `match_ended` fire in order; ELO, wins, streak, and `answers_data` persist accurately. |
| **Bot / Ghost Flow** | 1. Wait 60s in queue $\rightarrow$ receive `bot_offer`<br>2. Call `/api/matchmaking/switch-to-bot` with same `bot.id` as `player.id`<br>3. Play 10 questions with recorded `performance_data`, `advice_data=None`, and fallback questions | Bot answers at recorded delay; hints arrive when present; match ends with `0` ELO change and no ID collision. |
| **Invite Match Flow** | 1. Player 1 creates invite (`POST /api/matches/create-invite`)<br>2. Player 1 tries joining own code (rejected)<br>3. Player 2 joins code (`POST /api/matches/join-invite`) and both complete WebSocket match | Room code generated; 10 questions loaded; self-join blocked with `400`; full match completes cleanly. |
| **React Frontend UI & Hooks** | 1. `<AuthForm />` toggles Login/Register state and submits credentials<br>2. Protected routes (`/lobby`, `/battle/:matchId`) redirect unauthenticated users to `/auth`<br>3. `useLobbySocket` transitions to `/battle/:matchId` on `match_found` and opens `<BotOfferModal />` on `bot_offer`<br>4. `<BattlePage />` renders options, disables buttons after click, updates scores on `question_results`, and shows `<MatchResultModal />` on `match_ended` | Components render without console/state errors; WebSocket connections close cleanly on component unmount (`useEffect` cleanup). |

### 6.2 Load & Performance Testing (5,000 Concurrent Users Target)

Use **Locust** or **k6** to simulate concurrent HTTP and WebSocket traffic against the production deployment:

1. **Workload Mix (5,000 Virtual Users):**
   - **2,000 Lobby Users:** Authenticate, fetch dashboard/leaderboard, join matchmaking queue, maintain `/ws/lobby` connection.
   - **3,000 Active Battle Users (1,500 concurrent matches):** Maintain `/ws/match` connections, exchange `question_start`, `submit_answer`, and `question_results` every 10–15 seconds.
2. **Pass/Fail Service Level Objectives (SLOs):**
   - **REST API Latency:** `p95 < 150ms`, `p99 < 300ms` (excluding intentional bcrypt CPU time on `/api/login` and `/api/register` where `p95 < 500ms`).
   - **WebSocket Event Broadcast Latency:** `p95 < 50ms` from `submit_answer` receipt to `player_answered` / `question_results` broadcast.
   - **Event Loop Lag:** `< 20ms` max event loop delay during peak database commits at match end.
   - **Error Rate:** `< 0.1%` HTTP 5xx errors or unexpected WebSocket drops (`1006`/`1011`).
   - **Memory Footprint:** Zero memory leaks in `app.state.active_games`, `app.state.room_manager`, and `app.state.global_manager` after all 1,500 matches complete and disconnect.
