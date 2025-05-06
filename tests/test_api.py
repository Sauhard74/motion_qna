import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import init_db
from app.models.question import QuestionType, QuestionDifficulty

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_db():
    """Initialize database for tests."""
    init_db()
    yield
    # Here we could add cleanup after tests if needed


def test_read_root(setup_db):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.text.lower()


def test_create_question(setup_db):
    """Test creating a new question."""
    question_data = {
        "content": "What is the value of pi?",
        "type": QuestionType.MATH,
        "difficulty": QuestionDifficulty.EASY
    }
    response = client.post("/api/v1/questions/", json=question_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["content"] == question_data["content"]
    assert data["type"] == question_data["type"]
    assert data["difficulty"] == question_data["difficulty"]
    
    # Store question ID for future tests
    return data["id"]


def test_analyze_question(setup_db):
    """Test analyzing a question."""
    analysis_data = {
        "content": "What is the solution to 2x + 5 = 15?"
    }
    response = client.post("/api/v1/questions/analyze", json=analysis_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "type" in data
    assert "keywords" in data
    assert data["type"] == QuestionType.MATH  # Should detect as math question


def test_generate_hints(setup_db):
    """Test generating hints for a question."""
    # First create a question
    question_id = test_create_question(setup_db)
    
    # Generate hints
    hint_data = {
        "question_id": question_id,
        "num_hints": 2,
        "max_level": 2
    }
    response = client.post(f"/api/v1/questions/{question_id}/hints", json=hint_data)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= hint_data["num_hints"]
    
    for hint in data:
        assert "content" in hint
        assert "level" in hint
        assert hint["question_id"] == question_id


def test_generate_solution(setup_db):
    """Test generating a solution for a question."""
    # First create a question
    question_id = test_create_question(setup_db)
    
    # Generate solution
    solution_data = {
        "question_id": question_id,
        "step_by_step": True
    }
    response = client.post(f"/api/v1/questions/{question_id}/solution", json=solution_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "content" in data
    assert data["question_id"] == question_id 