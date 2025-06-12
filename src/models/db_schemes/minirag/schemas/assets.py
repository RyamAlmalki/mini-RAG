from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid 
from sqlalchemy.orm import relationship
from sqlalchemy import Index

class Assets(SQLAlchemyBase):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)  # Foreign key to the project this asset belongs to
    asset_type = Column(String, nullable=False)  # e.g., 'image', 'video', 'audio')
    asset_name = Column(String, nullable=False)  # e.g., 'image1.jpg', 'video1.mp4'
    asset_size = Column(Integer, nullable=False)  # Size in bytes
    asset_config = Column(JSONB, nullable=True) 

    project = relationship("Project", back_populates="assets")

    __table__args__ = (
        Index('idx_asset_project_id', 'asset_project_id'),
        Index('idx_asset_type', 'asset_type'),
    )

    # all the time you set this value 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # onupdate only when the row is updated you set this field to the current time
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)