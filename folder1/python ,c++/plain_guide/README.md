# SKYGUARD AI

SKYGUARD AI is a research-oriented flight-assistance simulation platform built with a FastAPI backend and a Vite + React cockpit dashboard.

## Overview

This project provides a simulated aviation operations dashboard with:

- live telemetry updates from a Python simulation engine
- simulated weather and turbulence data
- alert and monitoring panels
- assistant guidance for pilot-style queries
- a dark glass-cockpit UI theme

The platform is explicitly simulated and research-only. It does not represent certified flight operations or real aircraft control guidance.

## Stack

- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy + SQLite
- Simulation: Python telemetry engine

## Project structure

- `backend/` — FastAPI backend and simulation engine
- `frontend/` — React cockpit dashboard
- `.venv/` — local Python environment

## Run locally

### 1. Start the backend

From the project root:

```bash
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the frontend

From the `frontend/` directory:

```bash
npm install
npm run dev -- --host 0.0.0.0
```

## Available endpoints

- `GET /api/health`
- `GET /api/flight-status`
- `GET /api/weather`
- `GET /api/alerts`
- `POST /api/simulation/{action}`
- `POST /api/assistant/query`
- `GET /api/session-summary`
- `WS /ws/telemetry`

## Notes

- Simulation data is intentionally labeled as simulated.
- The app is intended for UX research and aviation dashboard prototyping.
- No real flight control actions or real-world operational decisions are provided.
