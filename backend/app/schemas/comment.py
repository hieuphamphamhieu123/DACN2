from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    username: str  # Joined from user data
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
