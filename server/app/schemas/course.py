from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LessonBase(BaseModel):
    title: str
    content: str
    order: int
    duration: Optional[str] = None

class LessonCreate(LessonBase):
    pass

class LessonResponse(LessonBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True

# Roadmap lesson (includes locked/unlocked status)
class RoadmapLesson(BaseModel):
    id: int
    title: str
    order: int
    duration: Optional[str] = None
    locked: bool
    completed: bool

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    price: float = 0.0
    difficulty_level: Optional[str] = None
    duration: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    difficulty_level: Optional[str] = None
    duration: Optional[str] = None

class TeacherInfo(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True

class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    created_at: datetime
    teacher: Optional[TeacherInfo] = None
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    course_id: int
    course_title: str
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    lessons: List[RoadmapLesson]
