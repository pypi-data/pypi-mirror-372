from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from .group import GroupInDB
class DocumentMetadata(BaseModel):
    size_bytes: Optional[int] = None
    language: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

class DocumentCreate(BaseModel):
    name: str
    user_document_id: Optional[str] = None
    owner_id: UUID
    access_group_id: Optional[UUID] = None
    is_public: bool = False
    metadata: Optional[DocumentMetadata] = None

class DocumentInDB(DocumentCreate):
    id: UUID = Field(default_factory=uuid4)
    access_group: Optional[GroupInDB] = None
    created: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    edited: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    # Поля из связанной таблицы stored_files
    is_sync_enabled: bool
    is_public: bool
    doc_type: str
    extension: str
    content_hash: str
    object_path: str

    class Config:
        from_attributes = True 
        
class Bibliography(BaseModel):
    doi: Optional[str] = None
    venue: Optional[str] = None
    publisher: Optional[str] = None
    affiliations: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    links: List[str] = Field(default_factory=list)

class SummaryIn(BaseModel):
    language: str = "ru"
    autors: List[str] = Field(default_factory=list)
    title: str = ""
    year: Optional[int] = None
    one_liner: str = ""
    # У вас extended_summary приходит строкой — так и валидируем
    extended_summary: Union[str, List[str]] = ""
    # У вас conclusions иногда строка — приведём к строке
    conclusions: Union[str, List[str]] = ""
    hashtags: List[str] = Field(default_factory=list)
    bibliography: Optional[Bibliography] = None

    @field_validator("autors", mode="before")
    @classmethod
    def _autors_to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, (list, tuple, set)):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, (str, bytes)):
            s = str(v).strip()
            return [s] if s else []
        return []

    @field_validator("year", mode="before")
    @classmethod
    def _coerce_year(cls, v):
        if v in (None, "", "null"):
            return None
        try:
            return int(v)
        except Exception:
            return None

    @field_validator("extended_summary", mode="before")
    @classmethod
    def _ext_sum_to_str(cls, v):
        if v is None:
            return ""
        if isinstance(v, (list, tuple)):
            return "\n\n".join(str(x).strip() for x in v if str(x).strip())
        return str(v).strip()

    @field_validator("conclusions", mode="before")
    @classmethod
    def _conclusions_to_str(cls, v):
        if v is None:
            return ""
        if isinstance(v, (list, tuple)):
            return "\n".join(str(x).strip() for x in v if str(x).strip())
        return str(v).strip()

    @field_validator("language", mode="after")
    @classmethod
    def _norm_lang(cls, v):
        return (v or "").strip() or "ru"