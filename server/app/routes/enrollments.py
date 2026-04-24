  # /enrollments endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..database import get_db
from ..models.enrollment import Enrollment
from ..models.progress import Progress
from ..models.lesson import Lesson
from ..models.course import Course
from ..models.user import User
from ..schemas.enrollment import (
    EnrollmentCreate, EnrollmentResponse,
    EnrollmentWithProgress, ProgressUpdate, ProgressResponse
)
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enroll in a course"""
    # Check course exists
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == data.course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")

    # Create enrollment
    # If course is free, mark payment as completed automatically
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=data.course_id,
        payment_completed=course.price == 0.0
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    # Create progress records for all lessons
    lessons = db.query(Lesson).filter(Lesson.course_id == data.course_id).all()
    for lesson in lessons:
        progress = Progress(
            enrollment_id=enrollment.id,
            lesson_id=lesson.id,
            completed=False
        )
        db.add(progress)
    db.commit()

    return enrollment

@router.get("/my", response_model=List[EnrollmentWithProgress])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all my enrolled courses with progress"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).all()

    result = []
    for enrollment in enrollments:
        lessons = db.query(Lesson).filter(
            Lesson.course_id == enrollment.course_id
        ).all()
        total = len(lessons)

        completed = db.query(Progress).filter(
            Progress.enrollment_id == enrollment.id,
            Progress.completed == True
        ).count()

        percentage = (completed / total * 100) if total > 0 else 0

        result.append(EnrollmentWithProgress(
            id=enrollment.id,
            course_id=enrollment.course_id,
            enrolled_at=enrollment.enrolled_at,
            payment_completed=enrollment.payment_completed,
            total_lessons=total,
            completed_lessons=completed,
            progress_percentage=round(percentage, 1)
        ))

    return result

@router.get("/{enrollment_id}/progress", response_model=List[ProgressResponse])
def get_progress(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific enrollment"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    progress = db.query(Progress).filter(
        Progress.enrollment_id == enrollment_id
    ).all()
    return progress

@router.post("/progress", response_model=ProgressResponse)
def mark_lesson_complete(
    data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a lesson as complete"""
    # Verify enrollment belongs to user
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == data.enrollment_id,
        Enrollment.user_id == current_user.id,
        Enrollment.payment_completed == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found or payment not completed")

    # Get progress record
    progress = db.query(Progress).filter(
        Progress.enrollment_id == data.enrollment_id,
        Progress.lesson_id == data.lesson_id
    ).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")

    # Check previous lesson is completed (roadmap logic)
    lesson = db.query(Lesson).filter(Lesson.id == data.lesson_id).first()
    if lesson.order > 1:
        prev_lesson = db.query(Lesson).filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order == lesson.order - 1
        ).first()
        if prev_lesson:
            prev_progress = db.query(Progress).filter(
                Progress.enrollment_id == data.enrollment_id,
                Progress.lesson_id == prev_lesson.id,
                Progress.completed == True
            ).first()
            if not prev_progress:
                raise HTTPException(
                    status_code=400,
                    detail="Complete previous lesson first"
                )

    # Mark as complete
    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(progress)
    return progress
