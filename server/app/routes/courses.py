from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.course import Course
from ..models.lesson import Lesson
from ..models.enrollment import Enrollment
from ..models.progress import Progress
from ..models.user import User
from ..schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    LessonCreate, LessonResponse, RoadmapResponse, RoadmapLesson
)
from ..utils.dependencies import get_current_user, require_teacher
from ..utils.security import decode_access_token

router = APIRouter(prefix="/courses", tags=["Courses"])

# ─── PUBLIC ENDPOINTS ────────────────────────────────────────────

@router.get("", response_model=List[CourseResponse])
def get_courses(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all courses (public)"""
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get single course details (public)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course

@router.get("/{course_id}/roadmap", response_model=RoadmapResponse)
def get_roadmap(
    course_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get course roadmap with locked/unlocked lesson status"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get lessons ordered by sequence
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id
    ).order_by(Lesson.order).all()

    completed_lesson_ids = set()

    # Try to get current user from token (optional)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                enrollment = db.query(Enrollment).filter(
                    Enrollment.user_id == int(user_id),
                    Enrollment.course_id == course_id,
                    Enrollment.payment_completed == True
                ).first()
                if enrollment:
                    completed_progress = db.query(Progress).filter(
                        Progress.enrollment_id == enrollment.id,
                        Progress.completed == True
                    ).all()
                    completed_lesson_ids = {p.lesson_id for p in completed_progress}

    # Build roadmap with locked/unlocked logic
    roadmap_lessons = []
    for i, lesson in enumerate(lessons):
        if i == 0:
            locked = False
        else:
            prev_lesson = lessons[i - 1]
            locked = prev_lesson.id not in completed_lesson_ids

        roadmap_lessons.append(RoadmapLesson(
            id=lesson.id,
            title=lesson.title,
            order=lesson.order,
            duration=lesson.duration,
            locked=locked,
            completed=lesson.id in completed_lesson_ids
        ))

    completed_count = len(completed_lesson_ids)
    total = len(lessons)
    percentage = (completed_count / total * 100) if total > 0 else 0

    return RoadmapResponse(
        course_id=course_id,
        course_title=course.title,
        total_lessons=total,
        completed_lessons=completed_count,
        progress_percentage=round(percentage, 1),
        lessons=roadmap_lessons
    )

# ─── TEACHER ENDPOINTS ───────────────────────────────────────────

@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Create a new course (Teacher only)"""
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        price=course_data.price,
        difficulty_level=course_data.difficulty_level,
        duration=course_data.duration,
        teacher_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Update a course (Teacher only, must be course owner)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    for field, value in course_data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Delete a course (Teacher only, must be course owner)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    db.query(Progress).filter(Progress.course_id == course_id).delete(synchronize_session=False)
    db.query(Enrollment).filter(Enrollment.course_id == course_id).delete(synchronize_session=False)
    db.query(Lesson).filter(Lesson.course_id == course_id).delete(synchronize_session=False)
    db.delete(course)
    db.commit()

@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def add_lesson(
    course_id: int,
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Add a lesson to a course (Teacher only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    new_lesson = Lesson(
        course_id=course_id,
        title=lesson_data.title,
        content=lesson_data.content,
        order=lesson_data.order,
        duration=lesson_data.duration
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    if enrollments:
        enrollment_ids = [enrollment.id for enrollment in enrollments]
        existing_progress_enrollment_ids = {
            progress.enrollment_id
            for progress in db.query(Progress).filter(
                Progress.lesson_id == new_lesson.id,
                Progress.enrollment_id.in_(enrollment_ids)
            ).all()
        }

        for enrollment in enrollments:
            if enrollment.id not in existing_progress_enrollment_ids:
                db.add(Progress(enrollment_id=enrollment.id, lesson_id=new_lesson.id))

        db.commit()

    return new_lesson

@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Update a lesson (Teacher only)"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    for field, value in lesson_data.model_dump().items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)
    return lesson

@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Delete a lesson (Teacher only)"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    db.query(Progress).filter(Progress.lesson_id == lesson_id).delete(synchronize_session=False)
    db.delete(lesson)
    db.commit()
