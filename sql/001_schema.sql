CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS dealers (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country_code CHAR(2) NOT NULL,
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    warranty_months INTEGER NOT NULL DEFAULT 0 CHECK (warranty_months >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY,
    dealer_id UUID NOT NULL REFERENCES dealers(id),
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    variant VARCHAR(150),
    price_eur_cents INTEGER NOT NULL CHECK (price_eur_cents > 0),
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    mileage_km INTEGER NOT NULL CHECK (mileage_km >= 0),
    fuel_type VARCHAR(40) NOT NULL,
    transmission VARCHAR(40) NOT NULL,
    body_type VARCHAR(40) NOT NULL,
    power_kw INTEGER CHECK (power_kw > 0),
    color VARCHAR(50),
    equipment JSONB NOT NULL DEFAULT '[]'::jsonb,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active','reserved','sold')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    dealer_id UUID REFERENCES dealers(id),
    vehicle_id UUID REFERENCES vehicles(id),
    title VARCHAR(300) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    s3_bucket VARCHAR(255) NOT NULL,
    s3_key VARCHAR(1024) NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    allowed_roles TEXT[] NOT NULL DEFAULT ARRAY['customer']::TEXT[],
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (s3_bucket, s3_key, version)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    token_count INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_vehicles_make_model ON vehicles (make, model);
CREATE INDEX IF NOT EXISTS idx_vehicles_price ON vehicles (price_eur_cents);
CREATE INDEX IF NOT EXISTS idx_vehicles_year_mileage ON vehicles (year, mileage_km);
CREATE INDEX IF NOT EXISTS idx_vehicles_fuel_body ON vehicles (fuel_type, body_type);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles (status);
CREATE INDEX IF NOT EXISTS idx_vehicles_equipment_gin ON vehicles USING GIN (equipment);
CREATE INDEX IF NOT EXISTS idx_documents_access ON documents USING GIN (allowed_roles);
CREATE INDEX IF NOT EXISTS idx_document_chunks_fts ON document_chunks USING GIN (content_tsv);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON document_chunks USING hnsw (embedding vector_cosine_ops);
