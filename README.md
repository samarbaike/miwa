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
| Database | TODO |
| Frontend / client | TODO |

## Architecture

Miwa is organized around a few core components:

- **API layer (FastAPI):** serves the HTTP endpoints for the application.
- **WebSocket layer:** keeps a persistent connection with each player so match events can be exchanged in real time.
- **Matchmaking:** takes players who want to play and groups them into matches.
- **Bot / GhostEngine:** provides the bot flows used when a match involves a simulated opponent.

TODO: add a short description of how a match moves from matchmaking to results, and how GhostEngine plugs into it.

## Getting started

```bash
# clone the repository
git clone https://github.com/samarbaike/miwa.git
cd miwa

# create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the development server
uvicorn <module>:app --reload
```

TODO: add environment variables, database setup, and the correct entry point.

## Project structure

TODO: add a short tree of the main folders and what each one contains.

## Roadmap

TODO: list planned features and improvements.