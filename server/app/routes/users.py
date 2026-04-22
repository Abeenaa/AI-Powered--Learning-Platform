# /users/profile endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.enrollment import Enrollment
from ..models.progress import Progress
from ..models.course import Course
from ..schemas.user import UserResponse, UserUpdate, UserStats
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
#  Get current user's profile.
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    
    return current_user

# Update current user's profile.
@router.put("/profile", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    # Only update fields that were actually sent
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user

#  Get current user's learning statistics
@router.get("/stats", response_model=UserStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all enrollments for this user
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).all()

    enrolled_count = len(enrollments)
    total_lessons = 0
    completed_lessons = 0

    # Count lessons and progress across all enrollments
    for enrollment in enrollments:
     # Count total lessons in this course
        course_lessons = db.query(Progress).filter(
            Progress.enrollment_id == enrollment.id
        ).count()
        total_lessons += course_lessons

    # Count completed lessons in this enrollment
        done = db.query(Progress).filter(
            Progress.enrollment_id == enrollment.id,
            Progress.completed == True
        ).count()
        completed_lessons += done

    # Calculate overall percentage
    overall = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    # Count courses created (for teachers)
    courses_created = db.query(Course).filter(
        Course.teacher_id == current_user.id
    ).count()

    return UserStats(
        enrolled_courses=enrolled_count,
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        overall_progress=round(overall, 1),
        courses_created=courses_created
    )
