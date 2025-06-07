from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id") 
    
    chunk_project_id: ObjectId
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)  
    
    class Config:
        # It's okay, I know what I'm doing — allow any type for fields, even if you don't have built-in validation for them.
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False,
            },
        ]