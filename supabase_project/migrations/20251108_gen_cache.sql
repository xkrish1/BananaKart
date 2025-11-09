create table if not exists public.gen_cache (
  id uuid primary key default gen_random_uuid(),
  key_hash text not null unique,
  query_text text not null,
  servings int not null,
  provider text not null,
  model text not null,
  response_json jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists gen_cache_created_at_idx on public.gen_cache(created_at desc);
create index if not exists gen_cache_key_hash_idx on public.gen_cache(key_hash);
