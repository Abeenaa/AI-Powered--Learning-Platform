# Lesson model
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)  #  For roadmap sequence
    duration = Column(String, nullable=True)  # e.g., "30 minutes"
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    progress_records = relationship("Progress", back_populates="lesson")
