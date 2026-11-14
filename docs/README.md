# docs

## Purpose

Project documentation that isn't tied to one folder: the architecture, the team's process
records, and the AI-use log the course requires.

## Contents

| File | What it holds | Updated when |
|---|---|---|
| `architecture.md` | Layer responsibilities (backend and frontend) and the feature-to-file map | A layer, rule, or feature file is added or changes role |
| `scrum.md` | Meeting notes, task split, decisions, and blockers per milestone | After each team meeting or milestone review |
| `PROVENANCE.md` | Numbered AI-use entries (student, artifact, label, tool, purpose, influence, validation, PR) | Before every PR that used AI |
| `agent_usage.md` | How to use AI agents here: what's set up, the skills, good habits, example requests | When a skill, agent rule, or tool setup changes |
| `team-agreement.md` | Empty | Never filled in |

## How it connects

- `AGENTS.md` points here for the full architecture; change `architecture.md`, not
  `AGENTS.md`, when the architecture changes.
- The root `README.md` links to `architecture.md` and lists every file here.
- PR descriptions disclose AI use and point to the matching `PROVENANCE.md` entry.
- Folder READMEs give each folder's details; `architecture.md` gives the whole picture.

## Conventions

- `PROVENANCE.md`: append only, next entry number, one entry per artifact or PR. Fill in the
  `PR:` line once the PR exists.
- `architecture.md` describes how the code *is*. Planned changes go in the issue or PR, not
  here.
- Not yet true: `architecture.md` names CSV persistence that doesn't exist and
  still lists the `MenuService` → `RestaurantRepository` exception that F18 removes;
  `team-agreement.md` is empty (F26).
