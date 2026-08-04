-- Structured query expected to return two active Golf listings.
SELECT
    v.id,
    v.make,
    v.model,
    v.price_eur_cents / 100.0 AS price_eur,
    v.mileage_km,
    d.name AS dealer_name,
    d.warranty_months
FROM vehicles v
JOIN dealers d ON d.id = v.dealer_id
WHERE v.status = 'active'
  AND lower(v.make) = 'volkswagen'
  AND lower(v.model) = 'golf'
  AND v.price_eur_cents <= 2000000
  AND v.mileage_km <= 80000
ORDER BY v.price_eur_cents;

-- Keyword retrieval test.
SELECT d.title, dc.chunk_index, ts_rank_cd(dc.content_tsv, query) AS rank, dc.content
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id,
     websearch_to_tsquery('english', 'return policy signed contract') query
WHERE dc.content_tsv @@ query
  AND 'customer' = ANY(d.allowed_roles)
ORDER BY rank DESC
LIMIT 5;

-- Vector retrieval template. Replace :query_embedding with a 1024-value vector.
-- SELECT d.title, dc.chunk_index, 1 - (dc.embedding <=> :query_embedding) AS similarity
-- FROM document_chunks dc
-- JOIN documents d ON d.id = dc.document_id
-- WHERE 'customer' = ANY(d.allowed_roles)
-- ORDER BY dc.embedding <=> :query_embedding
-- LIMIT 5;
