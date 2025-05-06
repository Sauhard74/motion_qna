from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuestionType(str, Enum):
    """Types of questions supported by the system."""
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    COMPUTER_SCIENCE = "computer_science"
    GENERAL_KNOWLEDGE = "general_knowledge"
    OTHER = "other"


class QuestionDifficulty(str, Enum):
    """Difficulty levels for questions."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Question(Base):
    """Question model representing a problem to be solved."""
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    type = Column(SQLEnum(QuestionType), default=QuestionType.OTHER, nullable=False)
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False)
    
    # Relationships
    solution = relationship("Solution", uselist=False, back_populates="question", cascade="all, delete-orphan")
    hints = relationship("Hint", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, type={self.type}, difficulty={self.difficulty})>"


class Solution(Base):
    """Solution model representing the answer to a question."""
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    content = Column(Text, nullable=False)
    steps = Column(Text, nullable=True)  # JSON-serialized steps for the solution
    
    # Relationships
    question = relationship("Question", back_populates="solution")
    
    def __repr__(self) -> str:
        return f"<Solution(id={self.id}, question_id={self.question_id})>"


class Hint(Base):
    """Hint model representing a hint for a question."""
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    content = Column(Text, nullable=False)
    level = Column(Integer, default=1, nullable=False)  # Difficulty level of the hint
    
    # Relationships
    question = relationship("Question", back_populates="hints")
    
    def __repr__(self) -> str:
        return f"<Hint(id={self.id}, question_id={self.question_id}, level={self.level})>" 