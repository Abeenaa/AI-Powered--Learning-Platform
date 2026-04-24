from pydantic import BaseModel
from datetime import datetime
from typing import List,Optional

class EnrollmentCreate(BaseModel):
    course_id:int

class ProgressUpdate(BaseModel):
    enrollment_id: int
    lesson_id: int
class ProgressResponse(BaseModel):
    id: int
    lesson_id: int
    completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    payment_completed: bool

    class Config:
        from_attributes = True


class EnrollmentWithProgress(BaseModel):
    id: int
    course_id: int
    enrolled_at: datetime
    payment_completed: bool
    total_lessons: int
    completed_lessons: int
    progress_percentage: float

    class Config:
        from_attributes = True