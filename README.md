# BananaKart

BananaKart pairs recipe personalisation with eco-aware supply chain estimates. The backend orchestrates tuned NLP inference, Monte Carlo simulations, and Supabase persistence, while the Vite frontend keeps the experience responsive for shoppers.

## Tech Stack

- FastAPI backend deployed on Render
- Vite + React frontend deployed on Vercel
- Supabase Postgres + storage for persistence
- Hugging Face Inference API for the tuned NLP model

## Repository Layout

- `apps/backend` – FastAPI service exposing `/analyze`
- `apps/frontend` – Vite client application
- `packages` – Shared Python utilities (simulation + NLP helpers)
- `supabase` – Database schema, seed data, and configuration

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase project credentials (service role key)
- Hugging Face API token with access to:
  - `xkrish/ingredient-ner-distilbert`
  - `xkrish/urgency-classifier-distilbert`

### Installation
```bash
git clone https://github.com/your-org/bananakart.git
cd bananakart

# Backend
python -m venv venv && source venv/bin/activate
pip install -r apps/backend/requirements.txt

# Frontend
cd apps/frontend
npm install
```

### Environment Configuration

Create `apps/backend/.env`:
```env
SUPABASE_URL=https://bkuszlqybwjpekstjapo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
HF_API_KEY=hf_<your_token>
USE_LOCAL_NLP=false
```

Create `apps/frontend/.env`:
```env
VITE_API_URL=https://bananakart.onrender.com
```

### NLP Smoke Test

Run the parser locally against the trained checkpoints (set `USE_LOCAL_NLP=true` to avoid pulling from the Hub):

```bash
USE_LOCAL_NLP=true python -c "from packages.nlp_engine.parser import parse; print(parse('make pasta with 200 g penne and 2 tbsp olive oil tonight'))"
```

### Running & Deployment

```bash
# Backend (development)
PYTHONPATH=. uvicorn apps.backend.main:app --reload

# Frontend (development)
cd apps/frontend
npm run dev
```

- Render deploys `apps/backend` automatically on push to `main`.
- Vercel deploys `apps/frontend` with the same branch. Ensure the environment variables above are set in the respective dashboards.

### Demo

- Production API: https://bananakart.onrender.com/analyze
- Hugging Face Space (interactive demo): https://huggingface.co/spaces/xkrish/bananakart

## Example API Usage

```bash
curl -X POST https://bananakart.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
        "user_id": "test-user",
        "recipe_text": "pasta with tomato sauce",
        "urgency": "tonight"
      }'
```

Example JSON response:

```json
{
  "status": "ok",
  "eco_score": 0.91,
  "co2_saved": 1.55,
  "variance_cost": 0.1,
  "recipe_id": "9f9580ac-6f9b-4ac0-8abc-9cc58f5b9f9b"
}
```

## Production Checklist

- Repo structure matches the monorepo layout (`apps`, `supabase`, `.env` files, `README.md`)
- Hugging Face credentials configured via `HF_API_KEY`
- Supabase tables `recipes` and `eco_results` contain the tuned model output
- Render and Vercel deployments succeed after each push to `main`