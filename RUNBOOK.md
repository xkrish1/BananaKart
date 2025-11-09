# BananaKart Hybrid Parser Runbook

## Required Environment Variables

- `HF_API_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_ORIGINS`
- `REQUEST_TIMEOUT_SECONDS`
- `HF_MAX_RETRIES`
- `RATE_LIMIT_PER_MINUTE`
- `GEN_MODEL`, `GEN_MAX_TOKENS`, `GEN_TEMPERATURE`, `GEN_DEFAULT_SERVINGS`, `GEN_CACHE_TTL_DAYS`

## Starting the Service

```bash
uvicorn apps.backend.main:app --reload
```

## Health Checks

- `POST /analyze_or_generate` with `"• 200 g penne\n• 2 tbsp olive oil"` → expect `mode="parse"`
- `POST /analyze_or_generate` with `"how to make spicy salsa"` → expect `mode="generate"`

## Common Failures

- **401 HF**: missing or invalid `HF_API_TOKEN`
- **429 HF**: upstream rate limit reached; retry/backoff engaged
- **429 API**: local rate limit exceeded (`RATE_LIMIT_PER_MINUTE`)
- **Supabase errors**: verify `SUPABASE_*` env settings and ensure `gen_cache` table exists

## Maintenance

- Run the cache cleanup migration periodically (e.g., Supabase Scheduled Function) to prune old rows
- Monitor logs for cache hit rate, generator fallbacks, and latency anomalies
