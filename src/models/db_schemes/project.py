from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    # When you create a new project, the _id will be optional
    # Use _id from the dict → store it in the model's id field.
    id: Optional[ObjectId] = Field(default=None, alias="_id") 
    project_id: str = Field(..., min_length=1)

    # Custom validation for project_id
    @field_validator("project_id")
    def validate_project_id(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return v
    
    class Config:
        # It's okay, I know what I'm doing — allow any type for fields, even if you don't have built-in validation for them.
        arbitrary_types_allowed = True