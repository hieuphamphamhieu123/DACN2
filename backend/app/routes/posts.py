from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.user import UserModel
from app.models.post import PostModel, ModerationResult
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    ModerationResultResponse
)
from app.utils.dependencies import get_current_user
from app.database import get_database
from app.utils.firestore_helpers import doc_to_dict, docs_to_list
from app.services.moderation_service import (
    content_moderation_service,
    image_moderation_service
)
from app.services.recommendation_service import recommendation_service

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new post with AI moderation
    """
    db = get_database()

    # Moderate text content
    moderation_result = await content_moderation_service.moderate_text(post_data.content)

    # Check if content should be blocked
    should_block = await content_moderation_service.should_block_content(moderation_result)

    # Moderate image if provided
    image_moderation_passed = True
    if post_data.image_url:
        image_result = await image_moderation_service.moderate_image(post_data.image_url)
        image_moderation_passed = image_result["passed"]

    # Create post document
    post_dict = {
        "user_id": current_user['id'],
        "content": post_data.content,
        "image_url": post_data.image_url,
        "tags": post_data.tags or [],
        "categories": post_data.categories or [],
        "moderation_result": moderation_result,
        "image_moderation_passed": image_moderation_passed,
        "is_approved": not should_block and image_moderation_passed,
        "likes_count": 0,
        "comments_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert post
    timestamp, doc_ref = db.collection('posts').add(post_dict)
    post_dict['id'] = doc_ref.id

    # Prepare response
    return PostResponse(
        id=post_dict['id'],
        user_id=str(post_dict["user_id"]),
        username=current_user['username'],
        content=post_dict["content"],
        image_url=post_dict.get("image_url"),
        tags=post_dict.get("tags", []),
        categories=post_dict.get("categories", []),
        moderation_result=ModerationResultResponse(**moderation_result) if moderation_result else None,
        image_moderation_passed=image_moderation_passed,
        is_approved=post_dict["is_approved"],
        likes_count=0,
        comments_count=0,
        created_at=post_dict["created_at"],
        updated_at=post_dict["updated_at"],
        is_liked_by_user=False
    )


@router.get("/", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get posts feed with optional filtering
    """
    db = get_database()

    # Build query
    # If filtering by user_id (profile page), show all posts (including pending approval)
    # Otherwise, only show approved posts
    if user_id:
        posts_ref = db.collection('posts').where('user_id', '==', user_id)
        # Don't use order_by here to avoid composite index requirement
        # Will sort in-memory instead
    else:
        posts_ref = db.collection('posts')\
            .where('is_approved', '==', True)\
            .order_by('created_at', direction='DESCENDING')

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        # Firestore requires array-contains for one tag at a time
        # For multiple tags, we'll filter in memory
        posts_ref = posts_ref.where('tags', 'array_contains', tag_list[0])

    if category:
        posts_ref = posts_ref.where('categories', 'array_contains', category)

    # Get all matching posts
    all_posts = list(posts_ref.stream())

    # Sort in-memory if user_id filter (to avoid composite index)
    if user_id:
        all_posts.sort(key=lambda x: doc_to_dict(x).get('created_at'), reverse=True)

    # Additional tag filtering if multiple tags
    if tags and len(tag_list) > 1:
        all_posts = [p for p in all_posts if any(tag in doc_to_dict(p).get('tags', []) for tag in tag_list)]

    total = len(all_posts)

    # Apply pagination
    skip = (page - 1) * page_size
    paginated_posts = all_posts[skip:skip + page_size]

    # Get user info and like status for each post
    post_responses = []
    for post_doc in paginated_posts:
        post = doc_to_dict(post_doc)

        # Get user info
        user_doc = db.collection('users').document(post["user_id"]).get()
        user = doc_to_dict(user_doc)
        username = user["username"] if user else "Unknown"

        # Check if current user liked this post
        like_docs = db.collection('likes')\
            .where('post_id', '==', post['id'])\
            .where('user_id', '==', current_user['id'])\
            .limit(1).stream()
        is_liked = len(list(like_docs)) > 0

        # Build response
        moderation_result = post.get("moderation_result")
        post_responses.append(PostResponse(
            id=post["id"],
            user_id=str(post["user_id"]),
            username=username,
            content=post["content"],
            image_url=post.get("image_url"),
            tags=post.get("tags", []),
            categories=post.get("categories", []),
            moderation_result=ModerationResultResponse(**moderation_result) if moderation_result else None,
            image_moderation_passed=post.get("image_moderation_passed", True),
            is_approved=post.get("is_approved", True),
            likes_count=post.get("likes_count", 0),
            comments_count=post.get("comments_count", 0),
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            is_liked_by_user=is_liked
        ))

    has_more = skip + page_size < total

    return PostListResponse(
        posts=post_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/feed", response_model=PostListResponse)
async def get_personalized_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get personalized feed based on user preferences AND liked posts
    AI learns from actual user behavior (likes) to improve recommendations
    """
    db = get_database()

    # Get all approved posts
    posts_ref = db.collection('posts')\
        .where('is_approved', '==', True)\
        .order_by('created_at', direction='DESCENDING')

    all_posts_docs = list(posts_ref.stream())
    all_posts = [doc_to_dict(doc) for doc in all_posts_docs]

    # Get posts that user has liked (for behavior-based learning)
    liked_posts = []
    try:
        likes_docs = db.collection('likes')\
            .where('user_id', '==', current_user['id'])\
            .stream()

        liked_post_ids = [doc_to_dict(doc)['post_id'] for doc in likes_docs]

        # Fetch the actual posts that were liked
        for post in all_posts:
            if post['id'] in liked_post_ids:
                liked_posts.append(post)
    except Exception as e:
        print(f"Warning: Failed to fetch liked posts: {e}")

    # Get user preferences
    preferences = current_user.get('preferences', {})
    user_preferences = {
        "favorite_tags": preferences.get('favorite_tags', []),
        "interests": preferences.get('interests', [])
    }

    # Get recommended posts (AI learns from both preferences AND likes)
    recommended_posts = await recommendation_service.get_recommended_posts(
        all_posts,
        user_preferences,
        liked_posts=liked_posts,  # Pass liked posts for behavior-based learning
        limit=page_size * 2  # Get more for pagination
    )

    # Apply pagination
    total = len(recommended_posts)
    skip = (page - 1) * page_size
    paginated_posts = recommended_posts[skip:skip + page_size]

    # Build responses
    post_responses = []
    for post in paginated_posts:
        # Get user info
        user_doc = db.collection('users').document(post["user_id"]).get()
        user = doc_to_dict(user_doc)
        username = user["username"] if user else "Unknown"

        # Check if current user liked this post
        like_docs = db.collection('likes')\
            .where('post_id', '==', post['id'])\
            .where('user_id', '==', current_user['id'])\
            .limit(1).stream()
        is_liked = len(list(like_docs)) > 0

        moderation_result = post.get("moderation_result")
        post_responses.append(PostResponse(
            id=post["id"],
            user_id=str(post["user_id"]),
            username=username,
            content=post["content"],
            image_url=post.get("image_url"),
            tags=post.get("tags", []),
            categories=post.get("categories", []),
            moderation_result=ModerationResultResponse(**moderation_result) if moderation_result else None,
            image_moderation_passed=post.get("image_moderation_passed", True),
            is_approved=post.get("is_approved", True),
            likes_count=post.get("likes_count", 0),
            comments_count=post.get("comments_count", 0),
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            is_liked_by_user=is_liked
        ))

    has_more = skip + page_size < total

    return PostListResponse(
        posts=post_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a single post by ID
    """
    db = get_database()

    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post = doc_to_dict(post_doc)

    # Get user info
    user_doc = db.collection('users').document(post["user_id"]).get()
    user = doc_to_dict(user_doc)
    username = user["username"] if user else "Unknown"

    # Check if current user liked this post
    like_docs = db.collection('likes')\
        .where('post_id', '==', post['id'])\
        .where('user_id', '==', current_user.id)\
        .limit(1).stream()
    is_liked = len(list(like_docs)) > 0

    moderation_result = post.get("moderation_result")
    return PostResponse(
        id=post["id"],
        user_id=str(post["user_id"]),
        username=username,
        content=post["content"],
        image_url=post.get("image_url"),
        tags=post.get("tags", []),
        categories=post.get("categories", []),
        moderation_result=ModerationResultResponse(**moderation_result) if moderation_result else None,
        image_moderation_passed=post.get("image_moderation_passed", True),
        is_approved=post.get("is_approved", True),
        likes_count=post.get("likes_count", 0),
        comments_count=post.get("comments_count", 0),
        created_at=post["created_at"],
        updated_at=post["updated_at"],
        is_liked_by_user=is_liked
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a post (only by owner)
    """
    db = get_database()

    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post = doc_to_dict(post_doc)

    # Check ownership
    if post["user_id"] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )

    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}

    if post_update.content is not None:
        # Re-moderate content if changed
        moderation_result = await content_moderation_service.moderate_text(post_update.content)
        should_block = await content_moderation_service.should_block_content(moderation_result)

        update_data["content"] = post_update.content
        update_data["moderation_result"] = moderation_result
        update_data["is_approved"] = not should_block and post.get("image_moderation_passed", True)

    if post_update.tags is not None:
        update_data["tags"] = post_update.tags

    if post_update.categories is not None:
        update_data["categories"] = post_update.categories

    # Update post
    db.collection('posts').document(post_id).update(update_data)

    # Get updated post
    updated_post_doc = db.collection('posts').document(post_id).get()
    updated_post = doc_to_dict(updated_post_doc)

    # Check if liked
    like_docs = db.collection('likes')\
        .where('post_id', '==', post_id)\
        .where('user_id', '==', current_user.id)\
        .limit(1).stream()
    is_liked = len(list(like_docs)) > 0

    moderation_result = updated_post.get("moderation_result")
    return PostResponse(
        id=updated_post["id"],
        user_id=str(updated_post["user_id"]),
        username=current_user['username'],
        content=updated_post["content"],
        image_url=updated_post.get("image_url"),
        tags=updated_post.get("tags", []),
        categories=updated_post.get("categories", []),
        moderation_result=ModerationResultResponse(**moderation_result) if moderation_result else None,
        image_moderation_passed=updated_post.get("image_moderation_passed", True),
        is_approved=updated_post.get("is_approved", True),
        likes_count=updated_post.get("likes_count", 0),
        comments_count=updated_post.get("comments_count", 0),
        created_at=updated_post["created_at"],
        updated_at=updated_post["updated_at"],
        is_liked_by_user=is_liked
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a post (only by owner)
    """
    db = get_database()

    post_doc = db.collection('posts').document(post_id).get()
    if not post_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post = doc_to_dict(post_doc)

    # Check ownership
    if post["user_id"] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )

    # Delete post
    db.collection('posts').document(post_id).delete()

    # Delete related likes
    likes_docs = db.collection('likes').where('post_id', '==', post_id).stream()
    for like_doc in likes_docs:
        like_doc.reference.delete()

    # Delete related comments
    comments_docs = db.collection('comments').where('post_id', '==', post_id).stream()
    for comment_doc in comments_docs:
        comment_doc.reference.delete()

    return None
