from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.user import UserModel
from app.models.comment import CommentModel
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from app.utils.dependencies import get_current_user
from app.database import get_database
from app.utils.firestore_helpers import doc_to_dict

router = APIRouter()


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a comment on a post
    """
    db = get_database()

    # Check if post exists
    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Create comment
    comment_dict = {
        "post_id": post_id,
        "user_id": current_user['id'],
        "content": comment_data.content,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    timestamp, doc_ref = db.collection('comments').add(comment_dict)
    comment_dict['id'] = doc_ref.id

    # Update post comments count
    post = doc_to_dict(post_doc)
    new_count = post.get('comments_count', 0) + 1
    db.collection('posts').document(post_id).update({'comments_count': new_count})

    return CommentResponse(
        id=comment_dict['id'],
        post_id=post_id,
        user_id=str(current_user['id']),
        username=current_user['username'],
        content=comment_dict["content"],
        created_at=comment_dict["created_at"],
        updated_at=comment_dict["updated_at"]
    )


@router.get("/{post_id}/comments", response_model=CommentListResponse)
async def get_comments(
    post_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all comments for a post
    """
    db = get_database()

    # Check if post exists
    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Get comments
    comments_ref = db.collection('comments')\
        .where('post_id', '==', post_id)\
        .order_by('created_at', direction='DESCENDING')
    comments_docs = list(comments_ref.stream())

    # Build responses with user info
    comment_responses = []
    for comment_doc in comments_docs:
        comment = doc_to_dict(comment_doc)
        user_doc = db.collection('users').document(comment["user_id"]).get()
        user = doc_to_dict(user_doc)
        username = user["username"] if user else "Unknown"

        comment_responses.append(CommentResponse(
            id=comment['id'],
            post_id=post_id,
            user_id=str(comment["user_id"]),
            username=username,
            content=comment["content"],
            created_at=comment["created_at"],
            updated_at=comment["updated_at"]
        ))

    return CommentListResponse(
        comments=comment_responses,
        total=len(comment_responses)
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a comment (only by owner)
    """
    db = get_database()

    comment_doc = db.collection('comments').document(comment_id).get()
    if not comment_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment = doc_to_dict(comment_doc)

    # Check ownership
    if comment["user_id"] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )

    # Update comment
    db.collection('comments').document(comment_id).update({
        "content": comment_update.content,
        "updated_at": datetime.utcnow()
    })

    # Get updated comment
    updated_comment_doc = db.collection('comments').document(comment_id).get()
    updated_comment = doc_to_dict(updated_comment_doc)

    return CommentResponse(
        id=updated_comment["id"],
        post_id=str(updated_comment["post_id"]),
        user_id=str(updated_comment["user_id"]),
        username=current_user['username'],
        content=updated_comment["content"],
        created_at=updated_comment["created_at"],
        updated_at=updated_comment["updated_at"]
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a comment (only by owner)
    """
    db = get_database()

    comment_doc = db.collection('comments').document(comment_id).get()
    if not comment_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment = doc_to_dict(comment_doc)

    # Check ownership
    if comment["user_id"] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )

    # Delete comment
    db.collection('comments').document(comment_id).delete()

    # Update post comments count
    post_doc = db.collection('posts').document(comment["post_id"]).get()
    if post_doc.exists:
        post = doc_to_dict(post_doc)
        new_count = max(0, post.get('comments_count', 1) - 1)
        db.collection('posts').document(comment["post_id"]).update({'comments_count': new_count})

    return None
