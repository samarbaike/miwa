# Miwa Frontend — Task 1 Implementation Guide
**Assignment:** HTML, CSS, DOM (Basic Structure & Plain JS/TS)  
**Project:** Miwa (Real-Time 1v1 ORT Quiz Platform)

---

## 1. Grading Alignment Matrix (Banking System $\rightarrow$ Miwa)

To ensure full marks from your professor, your Miwa frontend must include the exact same structural HTML/CSS/DOM mechanisms required in a standard banking application:

| Banking System Feature | Miwa Equivalent | Required HTML / CSS / DOM Concepts |
| :--- | :--- | :--- |
| **Account Login / Sign Up** | **Player Auth View** (`routes/auth.py`) | `<form>`, `<input>`, `<label>`, form validation, event listeners (`submit`). |
| **Account Balance Cards** | **ELO & Stats Overview** (`routes/user.py`) | `<section>`, `<article>`, CSS Grid / Flexbox layout, dynamic `textContent` updates. |
| **Money Transfer / Deposit** | **Matchmaking Queue Panel** (`routes/ws.py`) | `<select>`, radio inputs, primary action `<button>`, dynamic state toggling. |
| **Transaction History Table** | **Recent Matches Table** (`routes/matches.py`) | `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`, `document.createElement()` loop. |

---

## 2. Step 1: Repository Cleanup & Directory Setup

Before writing frontend code, clean up your repository root and create a dedicated `frontend/` workspace that won't clutter your FastAPI `app/` directory.

1. **Remove the tracked `websocat` binary from Git** (optional but recommended):
   ```bash
   echo "websocat" >> .gitignore
   git rm --cached websocat
   ```
2. **Create the `frontend/` directory and files** in the root of `samarbaike/miwa`:
   ```bash
   mkdir -p frontend
   touch frontend/index.html frontend/styles.css frontend/app.js
   ```
   *(Note: If you want to use TypeScript right away, name the script `app.ts` and compile it with `tsc app.ts`, or run `npm create vite@latest frontend -- --template vanilla-ts`.)*

---

## 3. Step 2: Build the Semantic HTML Structure (`frontend/index.html`)

To make your future transition to **React.js** effortless, build `index.html` as a **Single-Page Application (SPA) shell**. Each `<section>` represents what will later become a standalone React component (`<Navbar />`, `<Hero />`, `<AuthModal />`, `<LobbyDashboard />`).

### Detailed Checklist for `index.html`:

#### A. Document Boilerplate & `<header>`
* Set up a standard HTML5 document (`<!DOCTYPE html>`) linking `styles.css` in the `<head>` and `<script src="app.js" defer></script>` before `</body>`.
* Create a `<header class="navbar">` containing:
  * **Brand Logo/Title:** `<div class="logo">MIWA <span>ORT Arena</span></div>`
  * **Navigation Links (`<nav>`):** Three buttons with IDs for DOM switching:
    * `<button id="nav-home-btn" class="nav-btn active">Home</button>`
    * `<button id="nav-lobby-btn" class="nav-btn">Lobby</button>`
    * `<button id="nav-auth-btn" class="nav-btn btn-outline">Login / Register</button>`

#### B. View 1: Homepage / Hero Section (`#hero-view`)
* Create `<section id="hero-view" class="view-section">`.
* Add a main heading (`<h1>`), a short subtitle (`<p>`) explaining the 1v1 ELO-ranked ORT battles, and a `.hero-actions` container with two buttons:
  * `<button id="cta-play-btn" class="btn btn-primary">Play 1v1 Now</button>`
  * `<button id="cta-register-btn" class="btn btn-secondary">Create Account</button>`

#### C. View 2: Authentication Section (`#auth-view`)
* Create `<section id="auth-view" class="view-section hidden">`. *(Notice the `.hidden` class so it starts invisible).*
* Inside, create an `<article class="auth-card">` containing:
  * A dynamic header: `<h2 id="auth-title">Login to Miwa</h2>`
  * A `<form id="auth-form">`:
    * **Username Group:** `<label for="username">Username</label>` and `<input type="text" id="username" required placeholder="e.g. samarbaike" />`
    * **Email Group (For Registration):** Wrap in `<div id="email-group" class="form-group hidden">` so you can toggle it with JS when switching between Login and Register.
    * **Password Group:** `<label for="password">Password</label>` and `<input type="password" id="password" required />`
    * **Submit Button:** `<button type="submit" id="auth-submit-btn" class="btn btn-primary full-width">Sign In</button>`
  * A toggle paragraph at the bottom: `<p>Don't have an account? <a href="#" id="toggle-auth-mode">Register here</a></p>`

#### D. View 3: Player Lobby / Dashboard (`#lobby-view`)
* Create `<section id="lobby-view" class="view-section hidden">`.
* Divide this section into three distinct sub-blocks (mirroring a banking dashboard):

  1. **Player Stats Row (The "Account Balances" equivalent):**
     * Create `<div class="stats-grid">` containing three `<article class="stat-card">` elements:
       * **Card 1 (ELO Rating):** `<h3>Current ELO</h3>` + `<p id="stat-elo" class="stat-value">1200</p>` + `<span class="badge">Silver Division</span>`
       * **Card 2 (Matches Played):** `<h3>Matches Played</h3>` + `<p id="stat-matches" class="stat-value">24</p>`
       * **Card 3 (Win Rate):** `<h3>Win Rate</h3>` + `<p id="stat-winrate" class="stat-value">62.5%</p>`

  2. **Matchmaking Action Panel (The "Money Transfer" equivalent):**
     * Create `<article class="arena-panel">`.
     * Add a subject selector (`<select id="category-select">`) with options: `All ORT Subjects`, `Analogies & Sentence Completion`, `Reading Comprehension`, and `Math`.
     * Add a queue trigger button: `<button id="find-match-btn" class="btn btn-primary">Find 1v1 Opponent</button>`
     * Add a hidden status indicator: `<p id="queue-status" class="hidden">Searching for opponent near 1200 ELO... <span id="queue-timer">0s</span></p>`

  3. **Recent Match History Table (The "Transactions Table" equivalent):**
     * Create `<article class="history-panel">`.
     * Add `<h2>Recent Matches</h2>` and a filter dropdown or button (`All`, `Wins`, `Losses`).
     * Create a semantic `<table>`:
       ```html
       <table class="match-table">
         <thead>
           <tr>
             <th>Date</th>
             <th>Opponent</th>
             <th>Category</th>
             <th>Score</th>
             <th>Result</th>
             <th>ELO Change</th>
           </tr>
         </thead>
         <tbody id="match-history-body">
           <!-- Rows will be injected dynamically via DOM in app.js -->
         </tbody>
       </table>
       ```

---

## 4. Step 3: Write Clean, Modular CSS (`frontend/styles.css`)

Your professor will check for clean CSS layout techniques (Flexbox, CSS Grid, custom properties, and responsive design).

### Detailed Checklist for `styles.css`:

1. **CSS Variables (`:root`) & Reset:**
   * Define your theme variables at the top of the file so your UI looks like a modern competitive gaming/ed-tech app:
     ```css
     :root {
       --bg-dark: #0f172a;
       --bg-card: #1e293b;
       --text-main: #f8fafc;
       --text-muted: #94a3b8;
       --primary: #6366f1;       /* Indigo accent */
       --primary-hover: #4f46e5;
       --win-green: #10b981;     /* Positive ELO / Deposit equivalent */
       --loss-red: #ef4444;      /* Negative ELO / Withdrawal equivalent */
       --border-color: #334155;
     }
     ```
   * Apply `box-sizing: border-box; margin: 0; padding: 0;` to `*`.

2. **State Utility Classes:**
   * Create the `.hidden` class—this is crucial for plain JS DOM view-switching:
     ```css
     .hidden {
       display: none !important;
     }
     ```
   * Create classes for ELO changes in the table:
     ```css
     .elo-gain { color: var(--win-green); font-weight: 700; }
     .elo-loss { color: var(--loss-red); font-weight: 700; }
     ```

3. **Flexbox Navigation Bar (`.navbar`):**
   * Use `display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem;` with a bottom border (`1px solid var(--border-color)`).

4. **CSS Grid for Stats (`.stats-grid`):**
   * Use CSS Grid so the three ELO/stat cards sit side-by-side on desktop and stack automatically on mobile phones:
     ```css
     .stats-grid {
       display: grid;
       grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
       gap: 1.5rem;
       margin-bottom: 2rem;
     }
     ```

5. **Data Table Styling (`.match-table`):**
   * Set `width: 100%; border-collapse: collapse;`.
   * Add `padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid var(--border-color);` to `th` and `td`.
   * Add a subtle hover effect on table rows: `tbody tr:hover { background-color: rgba(255, 255, 255, 0.03); }`.

---

## 5. Step 4: Implement Plain JS/TS DOM Logic (`frontend/app.js`)

This is where you satisfy the **DOM Manipulation** requirement of the assignment. Do not use any frameworks yet—use native browser APIs (`querySelector`, `addEventListener`, `createElement`, `classList`).

### Detailed Checklist for `app.js`:

#### A. Mock State & Data (Simulating your FastAPI Backend)
At the top of `app.js`, define a mock user object and an array of recent matches (mirroring your `app/models/user.py` and `app/models/match.py` schemas):
```javascript
const currentUser = {
  username: "samarbaike",
  elo: 1245,
  matchesPlayed: 18,
  wins: 12
};

const matchHistory = [
  { date: "2026-10-25", opponent: "Ghost_Tilek", category: "Analogies", score: "8 - 6", result: "WIN", eloDiff: +16 },
  { date: "2026-10-24", opponent: "Aigerim_99", category: "Math", score: "5 - 7", result: "LOSS", eloDiff: -14 },
  { date: "2026-10-23", opponent: "Ghost_bek", category: "Vocabulary", score: "9 - 4", result: "WIN", eloDiff: +12 }
];
```

#### B. DOM View Switcher Function (SPA Router)
Write a reusable function `switchView(viewName)` that hides all `<section class="view-section">` elements by adding `.hidden`, and removes `.hidden` from the requested section:
* Wire `nav-home-btn` $\rightarrow$ `switchView('hero-view')`
* Wire `nav-lobby-btn` and `cta-play-btn` $\rightarrow$ `switchView('lobby-view')`
* Wire `nav-auth-btn` and `cta-register-btn` $\rightarrow$ `switchView('auth-view')`

#### C. Dynamic Auth Mode Toggle (Login $\leftrightarrow$ Register)
Attach a `click` listener to `#toggle-auth-mode`:
* Toggle a boolean `isRegisterMode`.
* Update `#auth-title.textContent` between `"Login to Miwa"` and `"Create a Miwa Account"`.
* Toggle the `.hidden` class on `#email-group`.
* Handle `#auth-form` submission (`e.preventDefault()`), read the `<input>` values, update `currentUser.username`, and automatically call `switchView('lobby-view')`.

#### D. Dynamic Table & Stats Rendering (`renderDashboard()`)
Write a function that populates the DOM using your mock data:
1. **Update Stat Cards:** Set `document.getElementById('stat-elo').textContent = currentUser.elo`, etc.
2. **Render Table Rows (`createElement`):**
   * Clear `#match-history-body.innerHTML = ''`.
   * Loop through `matchHistory` using `.forEach()`.
   * For each match, create a `const tr = document.createElement('tr')`.
   * Create `<td>` cells for Date, Opponent, Category, Score, Result, and ELO Change.
   * Apply `.elo-gain` if `match.eloDiff > 0` or `.elo-loss` if `match.eloDiff < 0`.
   * Append each `tr` to `#match-history-body`.

#### E. Interactive Matchmaking Simulation (Bonus DOM Manipulation)
Attach a `click` listener to `#find-match-btn`:
* Toggle `#queue-status` visibility.
* After 2 seconds (`setTimeout`), simulate a completed match: generate a random ELO change (e.g., `+15` or `-12`), update `currentUser.elo`, `.unshift()` a new match object into `matchHistory`, and re-run `renderDashboard()`.
* *(Why do this? In a banking assignment, clicking "Deposit $50" updates the balance card and adds a row to the transaction table. Clicking "Simulate Match" and watching ELO + Match History update live in the DOM is the exact 1-to-1 equivalent!)*

---

## 6. How This Prepares You for React.js Later

By following this exact structure in Task 1, when your professor introduces React in upcoming lectures:
1. Your **HTML sections** (`#hero-view`, `#auth-view`, `#lobby-view`) will copy-paste directly into JSX components (`Hero.jsx`, `AuthForm.jsx`, `LobbyDashboard.jsx`).
2. Your **`currentUser` and `matchHistory` objects** in `app.js` will become `useState()` hooks.
3. Your **`renderDashboard()` loop** will become a clean `matchHistory.map(match => <tr key={...}>)` inside JSX.
4. Your **`styles.css`** will work in React with zero changes required.