# BananaKart

Unified monorepo for the BananaKart platform. The repository contains the FastAPI backend and the Next.js/Vite frontend alongside shared packages and Supabase schema files.

## Repository Layout

- `apps/backend` – FastAPI application exposed on Render.
- `apps/frontend` – Public-facing frontend imported via git subtree (`green-kart-view`).
- `packages` – Reusable Python packages (NLP, simulation engine, shared utils).
- `supabase` – Database schema and seed scripts.

## Environment Variables

Environment configuration for both services is centralised in `.env.example`. Copy it to `.env` (backend) or `.env.local` (frontend) and populate the placeholders:

```env
# Backend (Render)
SUPABASE_URL=https://bkuszlqybwjpekstjapo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_key>
OPENWEATHER_KEY=<key>
TOMTOM_KEY=<key>

# Frontend (Vercel)
NEXT_PUBLIC_SUPABASE_URL=https://bkuszlqybwjpekstjapo.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
BACKEND_URL=https://bananakart-backend.onrender.com
MAPBOX_TOKEN=<mapbox_token>
```

Commit secrets to project dashboards only—never to git.

## Deployment

### Render (Backend)

- Render reads `render.yaml` at the repo root and deploys only the FastAPI service.
- Environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENWEATHER_KEY`, `TOMTOM_KEY`.
- Trigger a manual redeploy after merging frontend changes into `main`.

### Vercel (Frontend)

- Connect the same GitHub repository.
- Project Settings → Root Directory: `apps/frontend`.
- Configure environment variables: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `BACKEND_URL`, `MAPBOX_TOKEN`.

## Local Development

```bash
# Backend
PYTHONPATH=. uvicorn apps.backend.main:app --reload

# Frontend
cd apps/frontend
npm install
npm run dev
```

Visit `http://localhost:3000/analyze`, submit a recipe, and confirm requests reach the backend at `http://127.0.0.1:8000`.

## Production Verification Checklist

| Check                         | Status | Notes                                  |
| ----------------------------- | ------ | -------------------------------------- |
| Repo structure merged         | ☐      | `apps/frontend` present                |
| `.env.example` unified        | ☐      | Root file committed                    |
| Backend builds on Render      | ☐      | Verify `/health` returns 200           |
| Frontend builds on Vercel     | ☐      | Verify homepage loads                  |
| Frontend → Backend requests   | ☐      | Network tab shows successful API calls |
| CORS configuration            | ☐      | Origins include Vercel + bananakart.tech |
| Supabase write/read           | ☐      | Recipes + eco_results appear           |