# /ai endpoints (recommendations)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.enrollment import Enrollment
from ..models.course import Course
from ..models.lesson import Lesson
from ..models.progress import Progress
from ..models.user import User
from ..utils.dependencies import get_current_user
from ..services.ai_service import get_course_recommendations, get_next_lesson_suggestion

router = APIRouter(prefix="/ai", tags=["AI"])
#  Get AI-powered course recommendations.
@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    # Get user's enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).all()

    enrolled_course_ids = [e.course_id for e in enrollments]

    # Get enrolled course titles and progress
    enrolled_courses = []
    user_progress = {}

    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            enrolled_courses.append(course.title)

            # Calculate progress
            total = db.query(Progress).filter(
                Progress.enrollment_id == enrollment.id
            ).count()
            completed = db.query(Progress).filter(
                Progress.enrollment_id == enrollment.id,
                Progress.completed == True
            ).count()
            percentage = round((completed / total * 100), 1) if total > 0 else 0
            user_progress[course.title] = percentage

    # Get courses user hasn't enrolled in
    available_courses = db.query(Course).filter(
        Course.id.notin_(enrolled_course_ids)
    ).all()
    available_titles = [c.title for c in available_courses]

    # Get AI recommendations
    ai_suggestion = get_course_recommendations(
        enrolled_courses=enrolled_courses,
        available_courses=available_titles,
        user_progress=user_progress
    )

    return {
        "enrolled_courses": enrolled_courses,
        "available_courses": [
            {"id": c.id, "title": c.title, "price": c.price, "difficulty": c.difficulty_level}
            for c in available_courses
        ],
        "ai_recommendation": ai_suggestion or "Enroll in more courses to get personalized recommendations!"
    }

  #Get AI-powered suggestion for the next lesson.
@router.get("/next-lesson")
def get_next_lesson(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
  
    # Get enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        return {"message": "You are not enrolled in this course"}

    course = db.query(Course).filter(Course.id == course_id).first()

    # Get all lessons ordered
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id
    ).order_by(Lesson.order).all()

    # Get completed lessons
    completed_progress = db.query(Progress).filter(
        Progress.enrollment_id == enrollment.id,
        Progress.completed == True
    ).all()
    completed_ids = {p.lesson_id for p in completed_progress}
    completed_titles = [l.title for l in lessons if l.id in completed_ids]

    # Find next lesson
    next_lesson = None
    for lesson in lessons:
        if lesson.id not in completed_ids:
            next_lesson = lesson
            break

    if not next_lesson:
        return {
            "message": "Congratulations! You have completed all lessons!",
            "ai_tip": "You've finished this course! Consider enrolling in an advanced course."
        }

    # Calculate progress
    total = len(lessons)
    completed_count = len(completed_ids)
    percentage = round((completed_count / total * 100), 1) if total > 0 else 0

    # Get AI tip
    ai_tip = get_next_lesson_suggestion(
        course_title=course.title,
        completed_lessons=completed_titles,
        next_lesson=next_lesson.title,
        progress_percentage=percentage
    )

    return {
        "next_lesson": {
            "id": next_lesson.id,
            "title": next_lesson.title,
            "order": next_lesson.order,
            "duration": next_lesson.duration
        },
        "progress_percentage": percentage,
        "completed_lessons": completed_count,
        "total_lessons": total,
        "ai_tip": ai_tip or f"Ready for '{next_lesson.title}'? Keep going!"
    }
