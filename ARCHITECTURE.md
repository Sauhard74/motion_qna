# Motion Q&A: System Architecture

This document outlines the architecture and components of the Motion Q&A system, a platform for analyzing educational questions and generating hints and solutions.

## System Overview

Motion Q&A is built using a modern web architecture with the following key components:

1. **Web API**: FastAPI-based REST API
2. **AI Engine**: NLP models for question analysis and response generation
3. **Database**: Storage for questions, analyses, and generated content
4. **Web Interface**: Simple frontend for interaction with the system

## Component Architecture

### 1. Web API Layer

The API layer is built with FastAPI, providing:

- RESTful endpoint definitions
- Request validation with Pydantic schemas
- Automatic OpenAPI documentation
- Asynchronous request handling

Key files:
- `app/main.py`: Application entry point
- `app/api/v1/routes.py`: API endpoint definitions
- `app/api/schemas.py`: Pydantic models for request/response validation

### 2. AI Engine

The AI engine uses transformer-based models for NLP tasks and includes fallback template-based generation when transformers are not available:

- Question analysis: Determines question type, difficulty, and extracts keywords
- Hint generation: Provides progressive hints for educational value
- Solution generation: Creates step-by-step solutions

Key files:
- `app/services/ai_service.py`: Core AI functionality
- `app/services/custom_tokenizer.py`: Text processing utilities

#### AI Models Used

- **SentenceTransformer**: `paraphrase-MiniLM-L6-v2` for text embeddings
- **Text Generation**: `distilgpt2` for generating hints and solutions
- **Fallback**: Template-based generation when transformers are disabled

### 3. Database Layer

The database layer uses SQLAlchemy ORM with SQLite as the default backend:

- Stores questions, their metadata, and analysis results
- Tracks generated hints and solutions
- Provides data persistence between sessions

Key files:
- `app/models/question.py`: Database model definitions
- `app/services/db_service.py`: Database operations
- `app/core/setup.py`: Database initialization

### 4. Web Interface

A lightweight HTML/CSS/JavaScript frontend for direct interaction with the system:

- Question submission and analysis
- Hint and solution generation
- Display of results

Key files:
- `app/templates/*.html`: HTML templates
- `app/static/css/styles.css`: CSS styles
- `app/static/js/script.js`: Frontend JavaScript

## Request Flow

1. **Question Analysis**:
   - User submits a question
   - AI service analyzes the question to determine type and difficulty
   - Analysis results are returned and optionally stored in the database

2. **Hint Generation**:
   - User requests hints for a question
   - AI service generates appropriate hints based on question type
   - Hints are returned in a progressive sequence

3. **Solution Generation**:
   - User requests a solution for a question
   - AI service generates a step-by-step solution
   - Solution is formatted and returned to the user

## Architecture Diagram

```
┌─────────────┐         ┌───────────────┐        ┌──────────────┐
│             │         │               │        │              │
│  Web Client │ ◄─────► │  FastAPI App  │ ◄────► │  AI Service  │
│             │         │               │        │              │
└─────────────┘         └───────┬───────┘        └──────┬───────┘
                               │                        │
                               ▼                        │
                        ┌──────────────┐                │
                        │              │                │
                        │   Database   │ ◄──────────────┘
                        │              │
                        └──────────────┘
```

## Technical Implementation Details

### Question Analysis

Question analysis involves:
1. Text preprocessing (tokenization, stopword removal)
2. Embedding generation for semantic understanding
3. Classification of question type using similarity to type descriptions
4. Determination of difficulty level using multiple factors
5. Extraction of keywords and relevant concepts

### Hint Generation

Hint generation follows these steps:
1. Retrieve question metadata and analysis
2. Select appropriate hint templates based on question type
3. Generate hints using either transformer models or templates
4. Return hints in a progressive sequence from general to specific

### Solution Generation

Solution generation follows these steps:
1. Retrieve question metadata and analysis
2. Generate a step-by-step solution using either transformer models or templates
3. Format the solution with appropriate mathematical notation and explanations
4. Return the formatted solution

## Extensibility

The system is designed to be extensible in several ways:

1. **New Question Types**: Add new question types to the `QuestionType` enum and corresponding templates/analyzers
2. **Alternative Models**: Replace transformer models with alternatives by updating the model initialization
3. **Database Backends**: Switch database backends by changing the SQLAlchemy connection string
4. **API Extensions**: Add new endpoints to handle specialized question types or integrations

## Performance Considerations

1. **Model Loading**: Transformer models are loaded once at startup to avoid repeated loading overhead
2. **Template Fallback**: Template-based generation is available when transformer models are not suitable
3. **Resource Usage**: Command-line options allow disabling transformer models for resource-constrained environments
4. **Database Optimization**: SQLite is used for simplicity but can be replaced with more scalable solutions

## Security Considerations

1. **Input Validation**: All API inputs are validated using Pydantic schemas
2. **Rate Limiting**: Consider implementing rate limiting for production deployment
3. **Database Security**: Use parameterized queries (via SQLAlchemy) to prevent SQL injection
4. **Content Filtering**: Consider implementing content filtering for user inputs in production 