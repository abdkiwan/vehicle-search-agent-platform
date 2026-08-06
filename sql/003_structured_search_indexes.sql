CREATE INDEX IF NOT EXISTS idx_vehicles_make_model_ci
    ON vehicles (lower(make), lower(model));

CREATE INDEX IF NOT EXISTS idx_vehicles_active_price_mileage
    ON vehicles (price_eur_cents, mileage_km)
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_vehicles_active_year
    ON vehicles (year DESC)
    WHERE status = 'active';
