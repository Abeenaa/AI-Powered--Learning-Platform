# Progress model
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    enrollment = relationship("Enrollment", back_populates="progress_records")
    lesson = relationship("Lesson", back_populates="progress_records")
