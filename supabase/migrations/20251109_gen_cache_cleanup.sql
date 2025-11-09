-- keep recent cache entries based on configurable TTL
DO $$
DECLARE
  ttl_days INT := COALESCE(NULLIF(current_setting('app.gen_cache_ttl_days', true), '')::INT, 7);
BEGIN
  DELETE FROM public.gen_cache
  WHERE created_at < NOW() - (ttl_days || ' days')::INTERVAL;
END $$;
