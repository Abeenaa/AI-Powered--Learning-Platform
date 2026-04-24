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

# ─── TEACHER DASHBOARD ───────────────────────────────────────────

@router.get("/my-courses")
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all courses created by the teacher.
    Frontend uses this for the Teacher Dashboard to show their courses.
    Also shows how many students enrolled in each course.
    """
    courses = db.query(Course).filter(
        Course.teacher_id == current_user.id
    ).all()

    result = []
    for course in courses:
        student_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.payment_completed == True
        ).count()

        result.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "difficulty_level": course.difficulty_level,
            "duration": course.duration,
            "created_at": course.created_at,
            "enrolled_students": student_count,
            "total_lessons": len(course.lessons)
        })

    return result


@router.get("/my-courses/{course_id}/students")
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all students enrolled in a specific course.
    Frontend uses this for the Teacher Dashboard to manage students.
    Shows each student's progress in the course.
    """
    # Verify this course belongs to the teacher
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found or not yours")

    # Get all enrollments for this course
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.payment_completed == True
    ).all()

    students = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.user_id).first()
        if not student:
            continue

        # Get progress
        total = db.query(Progress).filter(
            Progress.enrollment_id == enrollment.id
        ).count()
        completed = db.query(Progress).filter(
            Progress.enrollment_id == enrollment.id,
            Progress.completed == True
        ).count()
        percentage = round((completed / total * 100), 1) if total > 0 else 0

        students.append({
            "student_id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "enrolled_at": enrollment.enrolled_at,
            "progress_percentage": percentage,
            "completed_lessons": completed,
            "total_lessons": total
        })

    return {
        "course_id": course_id,
        "course_title": course.title,
        "total_students": len(students),
        "students": students
    }
