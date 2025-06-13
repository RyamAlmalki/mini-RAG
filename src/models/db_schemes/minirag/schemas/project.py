from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid 
from sqlalchemy.orm import relationship

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # all the time you set this value 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # onupdate only when the row is updated you set this field to the current time
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # go to DataChunks you will find property project
    chunks = relationship("DataChunks", back_populates="project")

    # go to Assets you will find property project
    assets = relationship("Assets", back_populates="project")
