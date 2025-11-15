from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ModerationResultResponse(BaseModel):
    is_toxic: Optional[bool] = None
    is_spam: Optional[bool] = None
    is_hate_speech: Optional[bool] = None
    confidence_score: Optional[float] = None
    details: Optional[str] = None
    # Legacy fields for backward compatibility
    toxicity: Optional[float] = None
    severe_toxicity: Optional[float] = None
    obscene: Optional[float] = None
    threat: Optional[float] = None
    insult: Optional[float] = None
    identity_hate: Optional[float] = None
    passed: Optional[bool] = None

class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    image_url: Optional[str] = None
    tags: List[str] = []
    categories: List[str] = []

class PostUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None

class PostResponse(BaseModel):
    id: str
    user_id: str
    username: str  # We'll join this from user data
    content: str
    image_url: Optional[str] = None
    tags: List[str] = []
    categories: List[str] = []
    moderation_result: Optional[ModerationResultResponse] = None
    image_moderation_passed: bool = True
    is_approved: bool = True
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    updated_at: datetime
    is_liked_by_user: bool = False  # Whether current user liked this post

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
