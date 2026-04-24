# AI recommendations logic

def get_course_recommendations(
    enrolled_courses: list,
    available_courses: list,
    user_progress: dict
) -> str:
    """Smart course recommendations based on user's learning history."""
    if not available_courses:
        return "You've explored all available courses! Check back later for new content."

    if not enrolled_courses:
        return f"Welcome! We recommend starting with: {', '.join(available_courses[:3])}. These are great courses to kick off your learning journey!"

    completed_courses = [c for c, p in user_progress.items() if p == 100]
    in_progress = [c for c, p in user_progress.items() if 0 < p < 100]

    recommendation = []

    if in_progress:
        recommendation.append(f"You're currently working on: {', '.join(in_progress)}. Focus on completing these first!")

    if completed_courses:
        recommendation.append(f"Great job completing: {', '.join(completed_courses)}!")

    if available_courses:
        recommendation.append(f"Based on your progress, we recommend exploring: {', '.join(available_courses[:3])}.")

    return " ".join(recommendation) if recommendation else f"Consider enrolling in: {', '.join(available_courses[:2])}."


def get_next_lesson_suggestion(
    course_title: str,
    completed_lessons: list,
    next_lesson: str,
    progress_percentage: float
) -> str:
    """Personalized tip for the next lesson based on progress."""
    if progress_percentage == 0:
        return f"Welcome to '{course_title}'! Your first lesson '{next_lesson}' is ready. Take your time and enjoy the learning process!"

    if progress_percentage < 30:
        return f"Great start! You're {progress_percentage}% through '{course_title}'. '{next_lesson}' will build on what you've learned so far. Keep it up!"

    if progress_percentage < 60:
        return f"You're making solid progress at {progress_percentage}%! '{next_lesson}' is next - you're past the halfway point, keep pushing!"

    if progress_percentage < 90:
        return f"Almost there! At {progress_percentage}%, you're in the home stretch. '{next_lesson}' is one of the final steps - you've got this!"

    return f"Incredible! You're {progress_percentage}% done with '{course_title}'. Just '{next_lesson}' and a few more to go. Finish strong!"
