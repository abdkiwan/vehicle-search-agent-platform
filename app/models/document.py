from datetime import datetime
from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    JSONB,
    TSVECTOR,
    UUID as PG_UUID,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    dealer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dealers.id"),
    )

    vehicle_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id"),
    )

    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    s3_bucket: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    s3_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    allowed_roles: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1024),
        nullable=False,
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
    )

    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
    )

    content_tsv: Mapped[Any] = mapped_column(
        TSVECTOR,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )