from pydantic import BaseModel
from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid 
from sqlalchemy.orm import relationship
from sqlalchemy import Index


class DataChunks(SQLAlchemyBase):
    __tablename__ = "chunks"

    chunks_id = Column(Integer, primary_key=True, autoincrement=True)
    chunks_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    chunk_text = Column(String, nullable=False)  # The text content of the chunk
    chunk_metadata = Column(JSONB, nullable=True)  # Metadata associated with the chunk, e.g., source, timestamp
    chunk_order = Column(Integer, nullable=False)  # Order of the chunk in the document

    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)  # Foreign key to the project this chunk belongs to
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)  # Foreign key to the asset this chunk belongs to

    # all the time you set this value 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # onupdate only when the row is updated you set this field to the current time
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # go to Project you will find property chunks
    project = relationship("Project", back_populates="chunks")

    # go to Assets you will find property chunks
    assets = relationship("Assets", back_populates="chunks")


    __table__args__ = (
        Index('idx_chunk_project_id', 'chunk_project_id'),
        Index('idx_chunk_asset_id', 'chunk_asset_id'),
    )


class RetrievedDocuments(BaseModel):
    text: str
    score: float