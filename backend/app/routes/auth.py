from fastapi import APIRouter, HTTPException, status, Depends
from app.utils.dependencies import get_current_user
from datetime import timedelta
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.database import get_database
from app.config import settings
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    db = await get_database()
    
    # Check username exists
    if await db.users.find_one({"username": user_data.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check email exists
    if await db.users.find_one({"email": user_data.email}):
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
    
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    
    return UserResponse(**user_dict)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    db = await get_database()
    
    # Find user
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return UserResponse(**current_user)