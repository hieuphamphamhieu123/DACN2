from fastapi import APIRouter, HTTPException, status, Depends
from app.utils.dependencies import get_current_user
from datetime import timedelta
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse, UserPreferences, UserUpdate
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.database import get_database
from app.config import settings
from app.utils.firestore_helpers import doc_to_dict

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    db = get_database()

    # Check username exists
    users_ref = db.collection('users')
    existing_username = users_ref.where('username', '==', user_data.username).limit(1).get()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Check email exists
    existing_email = users_ref.where('email', '==', user_data.email).limit(1).get()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Create user
    user_dict = {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "bio": None,
        "avatar_url": None,
        "preferences": {"favorite_tags": [], "interests": []}
    }

    # Add document to Firestore
    timestamp, doc_ref = users_ref.add(user_dict)
    user_dict["id"] = doc_ref.id

    return UserResponse(**user_dict)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin):
    db = get_database()

    # Find user
    users_ref = db.collection('users')
    user_docs = users_ref.where('username', '==', user_data.username).limit(1).get()

    if not user_docs:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Get first (and only) user document
    user_doc = user_docs[0]
    user = user_doc.to_dict()
    user['id'] = user_doc.id

    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Create token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user['id']},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user)
):
    """Update user profile"""
    db = get_database()

    update_data = {}
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.bio is not None:
        update_data["bio"] = user_update.bio
    if user_update.avatar_url is not None:
        update_data["avatar_url"] = user_update.avatar_url

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Update user in Firestore
    users_ref = db.collection('users')
    users_ref.document(current_user['id']).update(update_data)

    # Get updated user
    updated_doc = users_ref.document(current_user['id']).get()
    updated_user = doc_to_dict(updated_doc)

    return UserResponse(**updated_user)

@router.put("/me/preferences", response_model=UserResponse)
async def update_preferences(
    preferences: UserPreferences,
    current_user = Depends(get_current_user)
):
    """Update user preferences for personalized recommendations"""
    db = get_database()

    preferences_dict = {
        "favorite_tags": preferences.favorite_tags,
        "interests": preferences.interests
    }

    # Update preferences in Firestore
    users_ref = db.collection('users')
    users_ref.document(current_user['id']).update({
        "preferences": preferences_dict
    })

    # Get updated user
    updated_doc = users_ref.document(current_user['id']).get()
    updated_user = doc_to_dict(updated_doc)

    return UserResponse(**updated_user)

@router.get("/me/preferences", response_model=UserPreferences)
async def get_preferences(current_user = Depends(get_current_user)):
    """Get user preferences"""
    preferences = current_user.get('preferences', {})
    return UserPreferences(
        favorite_tags=preferences.get('favorite_tags', []),
        interests=preferences.get('interests', [])
    )
