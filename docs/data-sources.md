# AI Vehicle Search — Data Sources Package

This package creates the first project layer:

- **Amazon RDS for PostgreSQL**: dealers, vehicles, document metadata, chunks, full-text index, and pgvector embeddings.
- **Amazon S3**: original Markdown documents as the source of truth.
- **Amazon Bedrock Titan Text Embeddings V2**: creates 1,024-dimensional embeddings during ingestion.

All companies, vehicles, policies, and prices are fictional test data.

## Package contents

- `data/structured/dealers.csv`: 5 fictional dealers.
- `data/structured/vehicles.csv`: 40 fictional vehicles.
- `data/unstructured/`: 18 help-center, dealer-policy, and vehicle-description documents.
- `data/unstructured/document_manifest.csv`: document IDs, RBAC roles, S3 keys, and checksums.
- `sql/001_schema.sql`: PostgreSQL and pgvector schema.
- `sql/002_verify_data.sql`: verification queries.
- `scripts/load_structured_data.py`: loads CSV data into RDS.
- `scripts/ingest_documents.py`: uploads Markdown files to S3, generates Bedrock embeddings, and indexes chunks in RDS.
- `evaluations/golden_queries.jsonl`: first evaluation cases tied to this dataset.

## Local preparation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

## Run after AWS resources exist

```bash
psql "$DATABASE_URL" -f sql/001_schema.sql
python scripts/load_structured_data.py
python scripts/ingest_documents.py
psql "$DATABASE_URL" -f sql/002_verify_data.sql
```
