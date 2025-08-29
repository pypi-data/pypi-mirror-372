# repositories/pg_repositoryBullets.py
from __future__ import annotations
from typing import Dict, List
from uuid import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sensory_data_client.db.documents.doc_bullet_orm import DocumentBulletORM
from sensory_data_client.db.base import get_session
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

class DocBulletsRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def save_flat_lists(
        self,
        doc_id: UUID,
        lists_map: Dict[str, List[str]],
        language: str = "ru",
        default_confidence: float = 0.9,
    ) -> int:
        """
        REPLACE-семантика:
        - для каждого (field_name, language) удаляем предыдущие записи этого списка,
          потом вставляем новые в правильном порядке без дублей.
        Возвращает количество созданных записей.
        """
        if not lists_map:
            return 0

        created = 0
        async with get_session(self._session_factory) as session:
            for field_name, items in (lists_map or {}).items():
                items = items or []
                # 1) удаляем старые записи списка (атомарно в рамках транзакции)
                await session.execute(
                    delete(DocumentBulletORM).where(
                        DocumentBulletORM.doc_id == doc_id,
                        DocumentBulletORM.field_name == field_name,
                        DocumentBulletORM.language == language,
                    )
                )
                if not items:
                    continue
                # 2) bulk insert
                values = []
                for i, text in enumerate(items):
                    values.append(
                        {
                            "doc_id": str(doc_id),
                            "field_name": field_name,
                            "text": (text or "").strip(),
                            "ord": i,
                            "language": language,
                            "confidence": float(default_confidence),
                            "line_ord": 0,
                        }
                    )
                stmt = pg_insert(DocumentBulletORM.__table__).values(values)
                await session.execute(stmt)
                created += len(values)
            await session.commit()
        return created

    async def attach_occurrence_range(
        self,
        bullet_id: UUID,
        start_line_id: UUID | None,
        end_line_id: UUID | None,
        page_start: int | None = None,
        page_end: int | None = None,
        ord: int = 0,
    ) -> DocumentBulletOccurrenceORM:
        async with get_session(self._session_factory) as session:
            occ = DocumentBulletOccurrenceORM(
                bullet_id=bullet_id,
                start_line_id=start_line_id,
                end_line_id=end_line_id,
                page_start=page_start,
                page_end=page_end,
                line_ord=ord,
            )
            session.add(occ)
            await session.commit()
            await session.refresh(occ)
            return occ