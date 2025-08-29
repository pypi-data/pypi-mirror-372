from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from sqlalchemy import Index, Boolean, text, Text, Integer
from sqlalchemy import String, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as PgEnum
import enum

from sensory_data_client.db.base import Base, CreatedAt, UpdatedAt
from sensory_data_client.models.document import DocumentInDB
from sensory_data_client.db.documents.document_permissions import DocumentPermissionORM
from sensory_data_client.db.tags.tag_orm import TagORM

class DocType(str, enum.Enum):
    generic = "generic"
    audio   = "audio"
    video   = "video"
    
class DocumentORM(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4) # ID на стороне сервера
    user_document_id: Mapped[str] = mapped_column(String, nullable=False) # ID на стороне клиента
    stored_file_id: Mapped[int] = mapped_column(
        ForeignKey("stored_files.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    
        # Новые поля для быстрой ориентации по документу
    # Язык документа (BCP-47/ISO, например "ru", "en")
    language: Mapped[Optional[str]] = mapped_column(String(16), index=True)
    # Авторы: список строк
    authors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text()), nullable=True)
    # Заголовок
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Год выпуска/публикации
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    # Короткая аннотация в одну строку
    one_liner: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Расширенное резюме списком
    extended_summary: Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    # Выводы/итоги списком
    conclusions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    #summary: Mapped[str] = mapped_column(String, nullable=False)
    # 'PRIVATE' - только владелец
    # 'GROUP' - доступ у группы, указанной в 'access_group_id'
    # 'SHARED' - доступ у явно перечисленных пользователей/групп в `permissions`
    # 'PUBLIC' - доступен всем аутентифицированным пользователям
    owner_id: Mapped[UUID] = mapped_column(PG_UUID, ForeignKey("users.id"), nullable=False, index=True)
    access_group_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID, ForeignKey("groups.id"), index=True)

    metadata_: Mapped[dict] = mapped_column("metadata", JSONB)
    
    created: Mapped[CreatedAt]
    edited: Mapped[UpdatedAt]
    
    is_sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"), comment="Флаг, разрешающий синхронизацию документа с Elasticsearch")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default=text("false"))
    
    doc_type: Mapped[str] = mapped_column(
        PgEnum(DocType, name="doc_type_enum"),
        server_default="generic",
        nullable=False
    )
    stored_file: Mapped["StoredFileORM"] = relationship("StoredFileORM", back_populates="documents", lazy="joined")
    tags: Mapped[List["TagORM"]] = relationship(
        secondary="document_tags", back_populates="documents", lazy="selectin"
    )
    
    owner: Mapped["UserORM"] = relationship("UserORM", back_populates="documents_owned")
    access_group: Mapped[Optional["GroupORM"]] = relationship("GroupORM", back_populates="documents", lazy="joined")
    permissions: Mapped[list["DocumentPermissionORM"]] = relationship("DocumentPermissionORM", back_populates="document", cascade="all, delete-orphan")
    
    raw_lines: Mapped[List["RawLineORM"]] = relationship(
            back_populates="document",
            cascade="all, delete-orphan",
            order_by="RawLineORM.position",
            lazy="select" 
        )
    
    image_lines: Mapped[List["ImageLineORM"]] = relationship(
        "ImageLineORM",
        back_populates="document", # Обратная связь в ImageLineORM будет называться "document"
        cascade="all, delete-orphan",
        lazy="selectin" # `selectin` - отличный выбор для быстрой загрузки
    )
    audio_lines: Mapped[List["AudioLineORM"]] = relationship(
        "AudioLineORM",
        back_populates="document", # Обратная связь в ImageLineORM будет называться "document"
        cascade="all, delete-orphan",
        lazy="selectin" # `selectin` - отличный выбор для быстрой загрузки
    )
    document_lines: Mapped[List["DocumentLineORM"]] = relationship(
        "DocumentLineORM",
        back_populates="document", # Обратная связь в ImageLineORM будет называться "document"
        cascade="all, delete-orphan",
        lazy="selectin" # `selectin` - отличный выбор для быстрой загрузки
    )
    bullets: Mapped[List["DocumentBulletORM"]] = relationship(
            "DocumentBulletORM", back_populates="document",
            cascade="all, delete-orphan", lazy="selectin"
        )
    
    __table_args__ = (
        UniqueConstraint("owner_id", "user_document_id", name="uq_documents_owner_userdoc"),
        Index("idx_documents_owner_id", "owner_id"),
        Index("idx_documents_access_group_id", "access_group_id"),
        Index("idx_documents_language", "language"),
        Index("idx_documents_year", "year"),
    )

    
    def to_pydantic(self) -> DocumentInDB:
        """
        Конвертирует ORM-объект в Pydantic-модель DocumentInDB.
        Берет поля content_hash и object_path из связанного объекта stored_file.
        """
        if not self.stored_file:
            raise ValueError("Cannot convert to Pydantic: stored_file relationship not loaded.")

        stored_file_data = {
            "extension": self.stored_file.extension,
            "content_hash": self.stored_file.content_hash,
            "object_path": self.stored_file.object_path,
        }

        return DocumentInDB.model_validate({**self.__dict__, **stored_file_data})
        
        