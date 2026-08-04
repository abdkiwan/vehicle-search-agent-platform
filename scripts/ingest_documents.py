from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

import boto3
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.environ["DATABASE_URL"]
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
S3_BUCKET = os.environ["S3_BUCKET"]
MODEL_ID = os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")

s3 = boto3.client("s3", region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def split_markdown(text: str, max_chars: int = 600) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def embed(text: str) -> list[float]:
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "inputText": text,
            "dimensions": 1024,
            "normalize": True,
        }),
    )
    payload = json.loads(response["body"].read())
    return payload["embedding"]


def main() -> None:
    manifest = ROOT / "data" / "unstructured" / "document_manifest.csv"
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        with manifest.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        for row in rows:
            local_path = ROOT / "data" / "unstructured" / row["relative_path"]
            content = local_path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if checksum != row["checksum_sha256"]:
                raise ValueError(f"Checksum mismatch: {local_path}")

            s3.upload_file(
                str(local_path),
                S3_BUCKET,
                row["s3_key"],
                ExtraArgs={
                    "ContentType": "text/markdown; charset=utf-8",
                    "Metadata": {
                        "document-id": row["id"],
                        "document-type": row["document_type"],
                    },
                },
            )

            allowed_roles = json.loads(row["allowed_roles"])
            conn.execute(
                """
                INSERT INTO documents (
                    id, dealer_id, vehicle_id, title, document_type,
                    s3_bucket, s3_key, checksum_sha256, version,
                    allowed_roles, language
                ) VALUES (
                    %(id)s, NULLIF(%(dealer_id)s, '')::uuid,
                    NULLIF(%(vehicle_id)s, '')::uuid, %(title)s,
                    %(document_type)s, %(s3_bucket)s, %(s3_key)s,
                    %(checksum_sha256)s, %(version)s, %(allowed_roles)s,
                    %(language)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    s3_bucket = EXCLUDED.s3_bucket,
                    s3_key = EXCLUDED.s3_key,
                    checksum_sha256 = EXCLUDED.checksum_sha256,
                    allowed_roles = EXCLUDED.allowed_roles
                """,
                {**row, "s3_bucket": S3_BUCKET, "allowed_roles": allowed_roles},
            )

            conn.execute("DELETE FROM document_chunks WHERE document_id = %s", (row["id"],))
            for index, chunk in enumerate(split_markdown(content)):
                chunk_id = str(uuid.uuid5(uuid.UUID(row["id"]), str(index)))
                vector = embed(chunk)
                conn.execute(
                    """
                    INSERT INTO document_chunks (
                        id, document_id, chunk_index, content, embedding,
                        token_count, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk_id,
                        row["id"],
                        index,
                        chunk,
                        vector,
                        None,
                        Jsonb({
                            "title": row["title"],
                            "document_type": row["document_type"],
                            "s3_key": row["s3_key"],
                        }),
                    ),
                )
            conn.commit()
            print(f"Uploaded and indexed: {row['relative_path']}")

        counts = conn.execute(
            "SELECT (SELECT COUNT(*) FROM documents), (SELECT COUNT(*) FROM document_chunks)"
        ).fetchone()
        print(f"Finished: {counts[0]} documents, {counts[1]} chunks.")


if __name__ == "__main__":
    main()
