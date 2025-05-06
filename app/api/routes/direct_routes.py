from fastapi import APIRouter, HTTPException, status

from app.api.schemas.question import HintRequest, GenerateSolutionRequest
from app.services.ai_service import AIService

# Create a separate router for direct generation
router = APIRouter(tags=["direct_generation"])

# Initialize AI service
ai_service = AIService()

@router.post("/generate-hints", status_code=status.HTTP_200_OK)
def generate_hints_directly(
    hint_request: HintRequest
):
    """Generate hints for a question without storing them."""
    if not hint_request.question_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question content is required for direct generation"
        )
        
    # Generate hints
    hint_data = ai_service.generate_hints(
        question_content=hint_request.question_content,
        num_hints=hint_request.num_hints,
        max_level=hint_request.max_level
    )
    
    return [{"content": hint["content"], "level": hint["level"]} for hint in hint_data]

@router.post("/generate-solution", status_code=status.HTTP_200_OK)
def generate_solution_directly(
    solution_request: GenerateSolutionRequest
):
    """Generate a solution for a question without storing it."""
    if not solution_request.question_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question content is required for direct generation"
        )
    
    question_content = solution_request.question_content
    
    # Try to solve as a basic equation first
    solution = ai_service._solve_basic_equation(question_content)
    
    # If equation solver worked, return those results
    if solution:
        return solution
        
    # Generate solution using the standard method if equation solver didn't work
    solution_data = ai_service.generate_solution(
        question_content=question_content,
        step_by_step=solution_request.step_by_step
    )
    
    return {
        "content": solution_data["content"],
        "steps": solution_data["steps"]
    }

@router.post("/solve-equation", status_code=status.HTTP_200_OK)
def solve_equation_directly(
    solution_request: GenerateSolutionRequest
):
    """Solve a mathematical equation directly."""
    if not solution_request.question_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equation is required"
        )
    
    # Try to solve as a basic equation
    solution = ai_service._solve_basic_equation(solution_request.question_content)
    
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not parse or solve the equation"
        )
        
    return solution 