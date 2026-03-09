# DeckForge Frontend

Single-page frontend for DeckForge backend.

## Stack

- React
- TypeScript
- Vite
- MUI

## Project structure

```text
src/
  app/
    theme.ts
  api/
    client.ts
    decks.ts
  types/
    decks.ts
  App.tsx
  main.tsx
```

## API contract used

- `POST /decks/`
  - request: `{ "words": ["string"], "options": {} }`
  - response: `{ "task_id": "uuid" }`
- `GET /decks/{task_id}/status`
  - response: `{ "status": "...", "items": [...] }`
- `GET /decks/{task_id}/result`
  - binary `.apkg` download

## UX flow

Single page, no routing:

1. Input
2. Processing (poll every 2.5 seconds)
3. Done (download + reset)

## Run

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

## Environment variables

- `VITE_API_BASE_URL` - API base URL used by frontend (default `/api`)
- `VITE_DEV_API_PROXY_TARGET` - backend URL for Vite proxy in development (default `http://localhost:8000`)

With default settings, requests go to `/api/*` and Vite forwards them to backend.
