-- Seed users
insert into public.users (id, email)
values
    ('72cf83a7-8d4c-4c99-874a-d88d16f0d0a0', 'chef.ana@example.com'),
    ('f35b6f44-10df-4b37-8ca7-5c6561d6e3bd', 'chef.raj@example.com')
on conflict (id) do nothing;

-- Seed recipes
insert into public.recipes (id, user_id, recipe_text, urgency)
values
    (
        '2d1593e3-13b4-4d7f-8afe-9dceb0b2adc7',
        (select id from public.users where email = 'chef.ana@example.com'),
        'Weeknight pasta primavera with seasonal vegetables',
        'tonight'
    ),
    (
        '9b27e9d7-03d5-47b6-9a8c-77e6607f6c95',
        (select id from public.users where email = 'chef.raj@example.com'),
        'Festive biryani with aromatic spices and saffron',
        'soon'
    )
on conflict (id) do nothing;

-- Seed ingredients
insert into public.ingredients (recipe_id, ingredient_name, quantity, unit)
values
    ((select id from public.recipes where id = '2d1593e3-13b4-4d7f-8afe-9dceb0b2adc7'), 'Spaghetti', 250, 'grams'),
    ((select id from public.recipes where id = '2d1593e3-13b4-4d7f-8afe-9dceb0b2adc7'), 'Cherry Tomatoes', 150, 'grams'),
    ((select id from public.recipes where id = '2d1593e3-13b4-4d7f-8afe-9dceb0b2adc7'), 'Asparagus', 120, 'grams'),
    ((select id from public.recipes where id = '9b27e9d7-03d5-47b6-9a8c-77e6607f6c95'), 'Basmati Rice', 300, 'grams'),
    ((select id from public.recipes where id = '9b27e9d7-03d5-47b6-9a8c-77e6607f6c95'), 'Saffron', 2, 'grams'),
    ((select id from public.recipes where id = '9b27e9d7-03d5-47b6-9a8c-77e6607f6c95'), 'Green Peas', 100, 'grams');

-- Seed suppliers
insert into public.suppliers (name, location, supplier_type, co2_per_km)
values
    ('FarmFresh Collective', 'Sonoma, CA', 'local', 0.8),
    ('Greenline Produce', 'Sacramento, CA', 'regional', 1.3),
    ('Spice Bazaar Central', 'Fremont, CA', 'local', 0.9),
    ('Wholesale Pantry Depot', 'Los Angeles, CA', 'big_box', 2.4)
on conflict (name) do nothing;

-- Seed eco results
insert into public.eco_results (
    recipe_id,
    eco_score,
    co2_saved_kg,
    variance_cost,
    best_sources,
    route_cluster
)
values
    (
        (select id from public.recipes where id = '2d1593e3-13b4-4d7f-8afe-9dceb0b2adc7'),
        0.82,
        5.4,
        -3.2,
        array['FarmFresh Collective', 'Greenline Produce'],
        'north_bay_low_emission'
    ),
    (
        (select id from public.recipes where id = '9b27e9d7-03d5-47b6-9a8c-77e6607f6c95'),
        0.74,
        4.1,
        1.8,
        array['Spice Bazaar Central', 'Wholesale Pantry Depot'],
        'bay_area_value_mix'
    );
