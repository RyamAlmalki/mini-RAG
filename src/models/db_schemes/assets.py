from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        # It's okay, I know what I'm doing — allow any type for fields, even if you don't have built-in validation for them.
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_project_id", 1)],
                "name": "asset_project_id_index_1",
                "unique": False,
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                "name": "asset_project_id_asset_name_index_1",
                "unique": True,
            },
        ]
          
  