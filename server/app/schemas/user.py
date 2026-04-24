from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"
    country: Optional[str] = None
# what frontend sends to register
class UserCreate(UserBase):
    password: str

#what fronted sends to login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
# what backend returns (no password)
class UserResponse(UserBase):
    id: int
    profile_picture: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
# Login response with JWT token
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
# For updating profile (all fields optional)
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    country: Optional[str] = None
    profile_picture: Optional[str] = None
# For dashboard stats
class UserStats(BaseModel):
    enrolled_courses: int        # How many courses student enrolled in
    completed_lessons: int       # Total lessons marked complete
    total_lessons: int           # Total lessons across all enrollments
    overall_progress: float      # Overall completion percentage
    courses_created: int         # For teachers: how many courses they created