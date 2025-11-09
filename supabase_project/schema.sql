-- Enable required extensions
create extension if not exists "pgcrypto";

-- Custom types
create type urgency_type as enum ('tonight', 'soon', 'later');
create type supplier_type as enum ('local', 'regional', 'big_box');

-- Tables
create table if not exists public.users (
    id uuid primary key default auth.uid(),
    email text unique not null,
    created_at timestamptz not null default now()
);

create table if not exists public.recipes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    recipe_text text not null,
    urgency urgency_type not null,
    created_at timestamptz not null default now()
);

create table if not exists public.ingredients (
    id serial primary key,
    recipe_id uuid not null references public.recipes(id) on delete cascade,
    ingredient_name text not null,
    quantity numeric not null,
    unit text not null
);

create table if not exists public.suppliers (
    id serial primary key,
    name text not null unique,
    location text not null,
    supplier_type supplier_type not null,
    co2_per_km numeric not null,
    created_at timestamptz not null default now()
);

create table if not exists public.eco_results (
    id serial primary key,
    recipe_id uuid not null references public.recipes(id) on delete cascade,
    eco_score numeric not null check (eco_score >= 0 and eco_score <= 1),
    co2_saved_kg numeric not null,
    variance_cost numeric not null,
    best_sources text[] not null,
    route_cluster text not null,
    created_at timestamptz not null default now()
);

-- Indexes
create index if not exists idx_recipes_user_id on public.recipes(user_id);
create index if not exists idx_ingredients_recipe_id on public.ingredients(recipe_id);
create index if not exists idx_eco_results_recipe_id on public.eco_results(recipe_id);

-- Row Level Security
alter table public.users enable row level security;
alter table public.recipes enable row level security;
alter table public.ingredients enable row level security;
alter table public.suppliers enable row level security;
alter table public.eco_results enable row level security;

-- Policies
create policy if not exists "recipe_ownership"
    on public.recipes
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

create policy if not exists "view_own_results"
    on public.eco_results
    for select
    using (exists (
        select 1
        from public.recipes r
        where r.id = eco_results.recipe_id
          and r.user_id = auth.uid()
    ));

-- Deny all other access by default; service role bypasses RLS.
