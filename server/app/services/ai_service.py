# AI recommendations logic
from openai import OpenAI
from ..config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

#     Uses OpenAI to recommend courses based on user's learning history.
def get_course_recommendations(
    enrolled_courses: list,
    available_courses: list,
    user_progress: dict
) -> str:
   
    if not settings.OPENAI_API_KEY:
        return None

    # Build context for OpenAI
    enrolled_str = ", ".join(enrolled_courses) if enrolled_courses else "none yet"
    available_str = ", ".join(available_courses) if available_courses else "none"
    progress_str = ", ".join([f"{k}: {v}%" for k, v in user_progress.items()]) if user_progress else "no progress yet"

    prompt = f"""You are a learning platform AI assistant.
    
A student is enrolled in: {enrolled_str}
Their progress: {progress_str}
Available courses they haven't enrolled in: {available_str}

Recommend 2-3 courses from the available list that would best complement their learning journey.
Be concise and explain why each course is recommended in one sentence.
If no courses are available, suggest what topics they should explore next."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content

#  Uses OpenAI to give personalized advice for the next lesson.
def get_next_lesson_suggestion(
    course_title: str,
    completed_lessons: list,
    next_lesson: str,
    progress_percentage: float
) -> str:
  
    if not settings.OPENAI_API_KEY:
        return None

    completed_str = ", ".join(completed_lessons) if completed_lessons else "none yet"

    prompt = f"""You are a helpful learning assistant.

A student is taking "{course_title}".
They have completed: {completed_str}
Their progress: {progress_percentage}%
Their next lesson is: "{next_lesson}"

Give them a short motivational tip (2-3 sentences) to prepare for their next lesson.
Be encouraging and specific to the lesson topic."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    return response.choices[0].message.content
