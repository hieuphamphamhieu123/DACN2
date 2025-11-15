from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.models.user import UserModel
from app.models.like import LikeModel
from app.schemas.like import LikeResponse
from app.utils.dependencies import get_current_user
from app.database import get_database
from app.utils.firestore_helpers import doc_to_dict

router = APIRouter()


@router.post("/{post_id}/like", response_model=LikeResponse)
async def toggle_like(
    post_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Toggle like on a post (like if not liked, unlike if already liked)
    """
    db = get_database()

    # Check if post exists
    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post = doc_to_dict(post_doc)

    # Check if already liked
    existing_likes = db.collection('likes')\
        .where('post_id', '==', post_id)\
        .where('user_id', '==', current_user['id'])\
        .limit(1).stream()

    existing_likes_list = list(existing_likes)

    if existing_likes_list:
        # Unlike: Remove like
        like_doc = existing_likes_list[0]
        like_doc.reference.delete()

        # Decrement likes count
        new_count = max(0, post.get('likes_count', 1) - 1)
        db.collection('posts').document(post_id).update({'likes_count': new_count})

        return LikeResponse(
            post_id=post_id,
            likes_count=new_count,
            is_liked=False
        )
    else:
        # Like: Create new like
        like_dict = {
            "post_id": post_id,
            "user_id": current_user['id'],
            "created_at": datetime.utcnow()
        }

        db.collection('likes').add(like_dict)

        # Increment likes count
        new_count = post.get('likes_count', 0) + 1
        db.collection('posts').document(post_id).update({'likes_count': new_count})

        return LikeResponse(
            post_id=post_id,
            likes_count=new_count,
            is_liked=True
        )


@router.get("/{post_id}/like", response_model=LikeResponse)
async def get_like_status(
    post_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get like status for a post
    """
    db = get_database()

    # Check if post exists
    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post = doc_to_dict(post_doc)

    # Check if user liked this post
    existing_likes = db.collection('likes')\
        .where('post_id', '==', post_id)\
        .where('user_id', '==', current_user['id'])\
        .limit(1).stream()

    is_liked = len(list(existing_likes)) > 0

    return LikeResponse(
        post_id=post_id,
        likes_count=post.get("likes_count", 0),
        is_liked=is_liked
    )
