# Roadmap Compliance Check (through Day 7)

This document records the current repository's alignment with **miwa_roadmap_v3.txt** up to and including **Day 7**.

## Summary by Day

| Day | Block | Expected Outcome (excerpt) | Status | Notes |
| --- | --- | --- | --- | --- |
| 1 | Scaffold | FastAPI app with `/` and `/health`; repo structure | ✅ Implemented (`app/main.py`, package layout) | Matches plan |
| 2 | Models | Database setup; BaseUser/Player/Admin; Question/MultipleChoice; Match enums; Bot | ✅ Present (`app/database.py`, `app/models/*.py`) | Structures match roadmap |
| 3 | Auth Foundations | User schemas; password hashing; AuthService.register; Session model | ✅ Present (`app/schemas/user.py`, `app/core/security.py`, `app/services/auth_service.py`, `app/models/session.py`) | Hashing via passlib; session table exists |
| 4 | DAA + Stats | `daa/data_structures.py` (Stack/Queue) and `applied-stats/ch02_indexing.ipynb` | ❌ Missing | No `daa/` or `applied-stats/` artifacts in repo |
| 5 | Rest | Free day | ✅ Not applicable | As planned |
| 6 | Rest | Free day | ✅ Not applicable | As planned |
| 7 | Stats + Auth Routes | `applied-stats/ch02_ranking.ipynb`; Auth routes for register/login with session cookie; `get_current_player` | ⚠️ Partial | Auth routes and dependency exist; ranking notebook absent |

## Block B (Day 7) Details
- **Routes**: `app/routes/auth.py` exposes `POST /api/register` and `POST /api/login`; `/api/user/me` uses `get_current_player`. Session cookie (`session_id`) is set on login and stored in `SessionTable`, matching the roadmap intent.
- **Auth service**: `AuthService.login` creates a session row with expiry; password verification uses bcrypt via passlib.
- **Dependency**: `get_current_player` validates the session token and returns the Player or raises 401, as required.
- **Gaps**:
  - Pydantic response models lack `orm_mode/model_config` configuration, so returning SQLAlchemy models may fail serialization in FastAPI.
  - Applied Stats notebook for ranking (`applied-stats/ch02_ranking.ipynb`) is absent.

## Outstanding Items to Align with Day 1-7
1. Add missing educational artifacts:  
   - `daa/data_structures.py` with Stack/Queue implementations and complexity notes.  
   - `applied-stats/ch02_indexing.ipynb` (Day 4) and `applied-stats/ch02_ranking.ipynb` (Day 7).
2. Harden Day 7 auth responses: enable ORM serialization on `UserResponse` (e.g., `model_config = {"from_attributes": True}`) to ensure register/login responses succeed.

This checklist can guide the next steps to reach full compliance for the first seven roadmap days.
