# BananaKart Hybrid Parser v0

- Adds `/analyze_or_generate` auto mode (generate or parse)
- Hugging Face Inference (Mistral-7B-Instruct) with strict JSON handling and retry
- Supabase `gen_cache` table with TTL and cleanup migration
- Backend hardening: CORS controls, timeouts, retries, in-memory rate limit
- Tests: NLP smoke covered in CI (now fails on errors)
- Default servings = 1 when unspecified; flagged in response payload

## Known Issues

- Rate limiting is per-process only; use Redis or an external store for multi-instance deployments
- Generator quality depends on prompt; keep `GEN_TEMPERATURE` ≤ 0.2 for best results
