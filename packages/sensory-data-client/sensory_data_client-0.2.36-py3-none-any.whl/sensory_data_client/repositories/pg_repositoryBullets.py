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
    ) -> int:
        if not lists_map:
            return 0

        created = 0
        cols = {c.name for c in DocumentBulletORM.__table__.columns}  # <-- какие колонки реально есть в БД

        async with get_session(self._session_factory) as session:
            for field_name, items in (lists_map or {}).items():
                items = items or []
                # можно подчистить старые записи этого списка/языка, если нужно REPLACE-семантику
                # await session.execute(delete(DocumentBulletORM).where(...))

                if not items:
                    continue

                values = []
                for i, text in enumerate(items):
                    row = {
                        "doc_id": str(doc_id),
                        "field_name": field_name,
                        "text": (text or "").strip(),
                        "ord": i,
                    }
                    if "language" in cols:
                        row["language"] = language
                    if "confidence" in cols:  # добавим позже, когда колонка появится
                        row["confidence"] = 0.9
                    if "line_ord" in cols:
                        row["line_ord"] = 0

                    values.append(row)

                stmt = pg_insert(DocumentBulletORM.__table__).values(values)
                await session.execute(stmt)
                created += len(values)

            await session.commit()
        return created