from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class ModerationResult(BaseModel):
    """AI moderation result for content"""
    is_toxic: bool = False
    is_spam: bool = False
    is_hate_speech: bool = False
    confidence_score: float = 0.0
    details: Optional[str] = None

class PostModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    content: str
    image_url: Optional[str] = None
    tags: List[str] = []
    categories: List[str] = []

    # AI Moderation Results
    moderation_result: Optional[ModerationResult] = None
    image_moderation_passed: bool = True
    is_approved: bool = True  # Auto-approve if moderation passes

    # Engagement metrics
    likes_count: int = 0
    comments_count: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
