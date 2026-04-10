# Miwa REST API Smoke Test Checklist

| Endpoint | Method | Request Body / Params | Expected Response | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
|`/api/matches/create-invite`|`POST`| Header: Cookie (Session) | `{"room_code": "A1B2C3"}` | Pass |
|`/api/register`|`POST`|Schema: UserRegister|User object|Pass|
|`/api/login`|`POST`| Schema: LoginRequest | `{"message": "Login successful"}` | Pass |
|`/api/user/me`|`GET`|Header: Cookie (Session)| User object | Pass |
|`/api/user/{user_id}`|`GET`|Path: id| User object | Pass |
|`/api/user/{user_id}`|`PUT`| Header: Cookie (Session), Path: id | User object | Pass |
|`/api/user/{user_id}`|`DELETE`|Header: Cookie(Session), Path: id|`{"message": "Oyunchu ochuruldu"}`|Pass|
|`/api/user/{user_id}/stats`|`GET`|Path: id|User object|Pass|
|`/api/leaderboard`|`GET`|None|List of User objects|Pass|
|`/api/match/{id}`|`GET`|Path: id|Match object|Pass|
|`/api/matchmaking/join`|`POST`|Header: Cookie(Session), Path: category|`{"status": "searching","message": "Kutuu bolmosuno koshtuk. Ataandash kutuudobuz."}`|Pass|