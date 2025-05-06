from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    HintCreate, HintResponse,
    SolutionCreate, SolutionResponse,
    QuestionAnalysisRequest, HintRequest, GenerateSolutionRequest
)
from app.core.database import get_db
from app.services.question_service import QuestionService
from app.services.ai_service import AIService

router = APIRouter(prefix="/questions", tags=["questions"])

# Initialize AI service
ai_service = AIService()


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question_in: QuestionCreate,
    db: Session = Depends(get_db)
):
    """Create a new question."""
    return QuestionService.create_question(db=db, question_in=question_in)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """Get a question by ID."""
    question = QuestionService.get_question(db=db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return question


@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get a list of questions."""
    return QuestionService.get_questions(db=db, skip=skip, limit=limit)


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    db: Session = Depends(get_db)
):
    """Update a question."""
    question = QuestionService.update_question(db=db, question_id=question_id, question_in=question_in)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """Delete a question."""
    success = QuestionService.delete_question(db=db, question_id=question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return None


@router.post("/analyze", status_code=status.HTTP_200_OK)
def analyze_question(
    analysis_request: QuestionAnalysisRequest
):
    """Analyze a question and return its characteristics."""
    analysis_result = ai_service.analyze_question(analysis_request.content)
    
    # If question type or difficulty is provided, override the detected values
    if analysis_request.type:
        analysis_result["type"] = analysis_request.type
    if analysis_request.difficulty:
        analysis_result["difficulty"] = analysis_request.difficulty
    
    return analysis_result


@router.post("/{question_id}/hints", response_model=List[HintResponse])
def create_hints(
    question_id: int,
    hint_request: HintRequest,
    db: Session = Depends(get_db)
):
    """Generate and store hints for a question."""
    # Check if question exists
    question = QuestionService.get_question(db=db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    # Generate hints
    hint_data = ai_service.generate_hints(
        question_content=question.content,
        num_hints=hint_request.num_hints,
        max_level=hint_request.max_level
    )
    
    # Save hints to database
    created_hints = []
    for hint in hint_data:
        hint_create = HintCreate(
            question_id=question_id,
            content=hint["content"],
            level=hint["level"]
        )
        created_hint = QuestionService.create_hint(db=db, hint_in=hint_create)
        created_hints.append(created_hint)
    
    return created_hints


@router.get("/{question_id}/hints", response_model=List[HintResponse])
def get_hints(
    question_id: int,
    db: Session = Depends(get_db)
):
    """Get all hints for a question."""
    # Check if question exists
    question = QuestionService.get_question(db=db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    return QuestionService.get_hints(db=db, question_id=question_id)


@router.post("/{question_id}/solution", response_model=SolutionResponse)
def create_solution(
    question_id: int,
    solution_request: GenerateSolutionRequest,
    db: Session = Depends(get_db)
):
    """Generate and store a solution for a question."""
    # Check if question exists
    question = QuestionService.get_question(db=db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    # Check if solution already exists
    existing_solution = QuestionService.get_solution(db=db, question_id=question_id)
    if existing_solution:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solution for question with ID {question_id} already exists"
        )
    
    # Generate solution
    solution_data = ai_service.generate_solution(
        question_content=question.content,
        step_by_step=solution_request.step_by_step
    )
    
    # Save solution to database
    solution_create = SolutionCreate(
        question_id=question_id,
        content=solution_data["content"],
        steps=solution_data["steps"]
    )
    return QuestionService.create_solution(db=db, solution_in=solution_create)


@router.get("/{question_id}/solution", response_model=SolutionResponse)
def get_solution(
    question_id: int,
    db: Session = Depends(get_db)
):
    """Get the solution for a question."""
    # Check if question exists
    question = QuestionService.get_question(db=db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    # Get solution
    solution = QuestionService.get_solution(db=db, question_id=question_id)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution for question with ID {question_id} not found"
        )
    
    return solution 