from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import auth,courses

app = FastAPI(
    title="Learning Platform API",
    description="AI-powered learning platform with roadmap-style courses",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)

@app.get("/")
def root():
    return {
        "message": "Learning Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }
