# AWS setup checklist

Use region `eu-central-1` (Frankfurt).

## 1. S3

Create a general-purpose bucket with a globally unique name such as:

`vehicle-search-context-<your-account-id>-eu-central-1`

Keep all Block Public Access settings enabled. Enable bucket versioning. The default SSE-S3 encryption is sufficient for the MVP; use SSE-KMS later if a customer-managed key is required.

## 2. RDS PostgreSQL

Create an RDS for PostgreSQL DB instance:

- Engine: PostgreSQL 16 or newer supported version
- Template: Dev/Test
- DB identifier: `vehicle-search-mvp`
- Initial database name: `vehicle_search`
- Master username: `postgres_admin`
- Credentials: Manage master credentials in AWS Secrets Manager
- Instance: smallest burstable class acceptable for your account and region
- Storage: 20 GiB gp3 with storage autoscaling
- Multi-AZ: No for this two-day MVP
- Public access: temporary Yes only if connecting directly from your laptop; restrict inbound TCP 5432 to your current public IP. Preferred production setup is private RDS accessed from ECS or a VPC-connected environment.
- Encryption: enabled
- Automated backups: 1–7 days for the MVP

After creation, connect as the master user and run `sql/001_schema.sql`.

Create a separate application user rather than using the master user:

```sql
CREATE USER vehicle_app WITH PASSWORD 'replace-with-a-strong-password';
GRANT CONNECT ON DATABASE vehicle_search TO vehicle_app;
GRANT USAGE ON SCHEMA public TO vehicle_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vehicle_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO vehicle_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO vehicle_app;
```

Store the application-user secret in Secrets Manager before deployment. Do not commit it to Git.

## 3. Bedrock

Confirm that `amazon.titan-embed-text-v2:0` is available in `eu-central-1`. The ingestion identity needs `bedrock:InvokeModel` for that model.

## 4. IAM for the ingestion script

For the MVP, run the script under your configured AWS CLI identity. It needs:

- `s3:PutObject`, `s3:GetObject`, and `s3:ListBucket` for the project bucket
- `bedrock:InvokeModel` for Titan Text Embeddings V2

The later ECS task role should receive the same permissions with resource scopes restricted to the project bucket and model.
