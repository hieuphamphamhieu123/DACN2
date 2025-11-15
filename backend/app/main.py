from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_firestore, close_firestore_connection, init_database
from app.routes import auth
from app.routes import posts
from app.routes import comments
from app.routes import likes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    await connect_to_firestore()
    await init_database()
    yield
    # Shutdown
    await close_firestore_connection()


app = FastAPI(title="Social Network API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/posts", tags=["Comments"])
app.include_router(likes.router, prefix="/api/posts", tags=["Likes"])

@app.get("/")
async def root():
    return {"message": "Social Network API", "status": "running"}