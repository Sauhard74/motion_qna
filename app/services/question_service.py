from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.question import Question, Solution, Hint
from app.api.schemas.question import (
    QuestionCreate, QuestionUpdate,
    SolutionCreate, HintCreate
)


class QuestionService:
    """Service for Question-related operations."""
    
    @staticmethod
    def create_question(db: Session, question_in: QuestionCreate) -> Question:
        """Create a new question in the database."""
        question = Question(
            content=question_in.content,
            type=question_in.type,
            difficulty=question_in.difficulty
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    
    @staticmethod
    def get_question(db: Session, question_id: int) -> Optional[Question]:
        """Get a question by ID."""
        return db.query(Question).filter(Question.id == question_id).first()
    
    @staticmethod
    def get_questions(db: Session, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get a list of questions."""
        return db.query(Question).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_question(db: Session, question_id: int, question_in: QuestionUpdate) -> Optional[Question]:
        """Update a question."""
        question = QuestionService.get_question(db, question_id)
        if not question:
            return None
        
        update_data = question_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        db.commit()
        db.refresh(question)
        return question
    
    @staticmethod
    def delete_question(db: Session, question_id: int) -> bool:
        """Delete a question."""
        question = QuestionService.get_question(db, question_id)
        if not question:
            return False
        
        db.delete(question)
        db.commit()
        return True
    
    @staticmethod
    def create_solution(db: Session, solution_in: SolutionCreate) -> Solution:
        """Create a solution for a question."""
        solution = Solution(
            question_id=solution_in.question_id,
            content=solution_in.content,
            steps=solution_in.steps
        )
        db.add(solution)
        db.commit()
        db.refresh(solution)
        return solution
    
    @staticmethod
    def get_solution(db: Session, question_id: int) -> Optional[Solution]:
        """Get the solution for a question."""
        return db.query(Solution).filter(Solution.question_id == question_id).first()
    
    @staticmethod
    def create_hint(db: Session, hint_in: HintCreate) -> Hint:
        """Create a hint for a question."""
        hint = Hint(
            question_id=hint_in.question_id,
            content=hint_in.content,
            level=hint_in.level
        )
        db.add(hint)
        db.commit()
        db.refresh(hint)
        return hint
    
    @staticmethod
    def get_hints(db: Session, question_id: int) -> List[Hint]:
        """Get all hints for a question."""
        return db.query(Hint).filter(Hint.question_id == question_id).order_by(Hint.level).all()
    
    @staticmethod
    def get_hint_by_level(db: Session, question_id: int, level: int) -> Optional[Hint]:
        """Get a specific hint by level for a question."""
        return db.query(Hint).filter(
            Hint.question_id == question_id,
            Hint.level == level
        ).first() 