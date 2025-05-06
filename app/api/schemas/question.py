from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.question import QuestionType, QuestionDifficulty
from app.core.enums import DifficultyLevel


# ---- Base models ----

class QuestionBase(BaseModel):
    """Base schema for Question."""
    content: str
    type: QuestionType = QuestionType.OTHER
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM


class HintBase(BaseModel):
    """Base schema for Hint."""
    content: str
    level: int = 1


class SolutionBase(BaseModel):
    """Base schema for Solution."""
    content: str
    steps: Optional[str] = None


# ---- Create models ----

class QuestionCreate(QuestionBase):
    """Schema for creating a new Question."""
    pass


class HintCreate(HintBase):
    """Schema for creating a new Hint."""
    question_id: int


class SolutionCreate(SolutionBase):
    """Schema for creating a new Solution."""
    question_id: int


# ---- Update models ----

class QuestionUpdate(BaseModel):
    """Schema for updating an existing Question."""
    content: Optional[str] = None
    type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None


class HintUpdate(BaseModel):
    """Schema for updating an existing Hint."""
    content: Optional[str] = None
    level: Optional[int] = None


class SolutionUpdate(BaseModel):
    """Schema for updating an existing Solution."""
    content: Optional[str] = None
    steps: Optional[str] = None


# ---- Response models ----

class HintResponse(HintBase):
    """Schema for Hint response."""
    id: int
    question_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SolutionResponse(SolutionBase):
    """Schema for Solution response."""
    id: int
    question_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionResponse(QuestionBase):
    """Schema for Question response."""
    id: int
    created_at: datetime
    updated_at: datetime
    hints: List[HintResponse] = []
    solution: Optional[SolutionResponse] = None

    class Config:
        from_attributes = True


# ---- Service models ----

class QuestionAnalysisRequest(BaseModel):
    """Schema for question analysis request."""
    content: str = Field(..., description="The question to analyze")
    type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None


class HintRequest(BaseModel):
    """Schema for hint generation request."""
    question_id: Optional[int] = Field(None, description="ID of the question to generate hints for")
    question_content: Optional[str] = Field(None, description="Content of the question to generate hints for (used for direct generation)")
    num_hints: int = Field(1, description="Number of hints to generate")
    max_level: int = Field(3, description="Maximum hint level (difficulty)")


class GenerateSolutionRequest(BaseModel):
    """Schema for solution generation request."""
    question_id: Optional[int] = Field(None, description="ID of the question to generate a solution for")
    question_content: Optional[str] = Field(None, description="Content of the question to generate a solution for (used for direct generation)")
    step_by_step: bool = Field(True, description="Whether to generate a step-by-step solution") 