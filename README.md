# Motion Q&A: Question Analysis and Solution Generation System

A system that analyzes questions, particularly in educational contexts, and generates appropriate hints and solutions.

## Features

- Question parsing and analysis
- Automatic hint generation for learning assistance
- Step-by-step solution generation
- API endpoints for integration with educational platforms
- Web interface for easy interaction

## Technology Stack

- **Backend**: Python 3.9+, FastAPI
- **Database**: SQLite (easily replaceable with other SQL databases)
- **NLP**: Transformer-based models or template-based generation
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker

## Getting Started

### Prerequisites

- Python 3.9+
- pip
- Docker (optional, for containerized deployment)

### Option 1: Direct Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/motion_qna.git
cd motion_qna
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
# Initialize the database and start the server
python run.py
```

4. For development with auto-reload:
```bash
python run.py --reload
```

5. To disable transformer models (faster startup, template-based generation):
```bash
python run.py --no-models
```

### Option 2: Docker Deployment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/motion_qna.git
cd motion_qna
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. The application will be available at: http://localhost:8000

### Running Tests

Run the test suite:
```bash
python test.py
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Usage

### Web Interface

1. Open your browser and navigate to: http://localhost:8000
2. Enter a question in the text area
3. Select the question type and difficulty (or let the system detect it)
4. Click "Analyze Question" to see an analysis of the question
5. Click "Submit Question" to store the question
6. Generate hints or solutions using the respective buttons

### API Endpoints

- `POST /api/v1/questions/analyze`: Analyze a question
- `POST /api/v1/questions/`: Create a new question
- `GET /api/v1/questions/{question_id}`: Get a question by ID
- `POST /api/v1/questions/{question_id}/hints`: Generate hints
- `POST /api/v1/questions/{question_id}/solution`: Generate a solution

## Project Structure

```
motion_qna/
├── app/                 # Main application code
│   ├── api/             # API endpoints and schemas
│   ├── core/            # Core configuration and setup
│   ├── models/          # Database models
│   ├── services/        # Business logic services
│   ├── static/          # Static files (CSS, JS)
│   └── templates/       # HTML templates
├── tests/               # Test suite
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker configuration
├── requirements.txt     # Project dependencies
├── run.py               # Application runner
└── test.py              # Test runner
```

## Development Considerations

### Adding New Question Types

To add support for a new question type:

1. Add the new type to the `QuestionType` enum in `app/models/question.py`
2. Update the analysis logic in `app/services/ai_service.py`
3. Add appropriate templates for hints and solutions

### Customizing Templates

The template-based generation system uses predefined templates in `app/services/ai_service.py`. You can customize these templates to better suit specific question types.

### Using Different ML Models

By default, the system can use the `gpt2` model from Hugging Face Transformers. To use a different model:

1. Update the `DEFAULT_MODEL` setting in `app/core/config.py`
2. Ensure the new model is compatible with the text generation pipeline

## License

MIT

## Acknowledgements

- FastAPI for the web framework
- SQLAlchemy for the ORM
MIT 