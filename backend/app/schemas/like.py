from pydantic import BaseModel

class LikeResponse(BaseModel):
    post_id: str
    likes_count: int
    is_liked: bool

    class Config:
        from_attributes = True
