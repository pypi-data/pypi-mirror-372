# db/documents/doc_bullet_orm.py
from __future__ import annotations
from uuid import UUID, uuid4
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Float, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sensory_data_client.db.base import Base, CreatedAt, UpdatedAt

class DocumentBulletORM(Base):
    __tablename__ = "doc_bullets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    doc_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True),
                                         ForeignKey("documents.id", ondelete="CASCADE"),
                                         nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String, nullable=False, index=True)  # например: "methods", "key_points"
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ord: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # порядок в исходном списке

    # # Язык конкретного списка (важно для мультиязычных документов)
    language: Mapped[str] = mapped_column(String(16), nullable=False, server_default="ru", index=True)
    # # Уверенность в извлечении/описании
    # confidence: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.9")

    start_line_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True),
                                                          ForeignKey("raw_lines.id", ondelete="CASCADE"),
                                                          nullable=True, index=True)
    end_line_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True),
                                                        ForeignKey("raw_lines.id", ondelete="CASCADE"),
                                                        nullable=True, index=True)

    # Альтернативно можно заранее указывать конкретные линии списком (через ord + мультизаписи)
    line_ord: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    document = relationship("DocumentORM", back_populates="bullets")
    occurrences: Mapped[List["DocumentBulletOccurrenceORM"]] = relationship(
        "DocumentBulletOccurrenceORM", back_populates="bullet",
        cascade="all, delete-orphan", lazy="selectin"
    )
    start_line = relationship("RawLineORM", foreign_keys=[start_line_id], lazy="selectin")
    end_line = relationship("RawLineORM", foreign_keys=[end_line_id], lazy="selectin")

    __table_args__ = (
        Index("idx_doc_bullets_doc_id_field", "doc_id", "field_name"),
        Index("idx_doc_bullet_occ_start_line", "start_line_id"),
        Index("idx_doc_bullet_occ_end_line", "end_line_id"),
    )

