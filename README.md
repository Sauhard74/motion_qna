# Motion Q&A

A question analysis and solution generation system for educational content.

<img width="1480" alt="Screenshot 2025-05-06 at 6 24 47 PM" src="https://github.com/user-attachments/assets/a7864403-89d1-4b50-810f-21e814ed49d6" />
<img width="1512" alt="Screenshot 2025-05-06 at 6 24 54 PM" src="https://github.com/user-attachments/assets/4100b8da-7c16-42e1-861d-3c1f10d3174e" />

## Overview

Motion Q&A is an AI-powered application that helps students with educational questions in various subjects including mathematics, physics, chemistry, biology, and computer science. The application can:

- Analyze questions
- Generate customized hints with varying levels of detail
- Provide step-by-step solutions

## Features

- **Multi-Subject Support**: Math, Physics, Chemistry, Biology, Computer Science, and more
- **Difficulty Levels**: Easy, Medium, Hard, Expert
- **Hint Generation**: Progressive hints that guide without giving away the complete solution
- **Step-by-Step Solutions**: Detailed solutions with explanations
- **Clean UI**: Simple and intuitive interface for question submission and analysis
- **API Support**: RESTful API for integration with other systems

## Getting Started

### Prerequisites

- Python 3.9+
- NLTK resources (stopwords, punkt)
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/motion_qna.git
   cd motion_qna
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Install NLTK resources
   ```bash
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
   ```

4. Initialize the database
   ```bash
   python -c "from app.core.setup import initialize_app; initialize_app()"
   ```

### Running Locally

```bash
python run.py --host localhost --port 8000
```

For lightweight deployment without heavy ML models:

```bash
python run.py --host localhost --port 8000 --no-models
```

### Docker Deployment

#### Using the Deployment Script

We provide a convenient deployment script to manage the Docker container:

```bash
# Make the script executable (first time only)
chmod +x deploy.sh

# Show available commands
./deploy.sh help

# Build the Docker image
./deploy.sh build

# Start the container
./deploy.sh start

# Check container status
./deploy.sh status

# View logs
./deploy.sh logs

# Rebuild and restart the container
./deploy.sh rebuild

# Stop the container
./deploy.sh stop

# Clean up Docker resources
./deploy.sh clean
```

#### Manual Docker Commands

1. Build the Docker image
   ```bash
   docker build -t motion_qna:latest .
   ```

2. Run the container
   ```bash
   docker run -d -p 8000:8000 --name motion_qna_app motion_qna:latest
   ```

3. Access the application at http://localhost:8000

## API Usage

### Submit a Question

```bash
curl -X POST "http://localhost:8000/api/v1/questions/" \
  -H "Content-Type: application/json" \
  -d '{"content":"solve x: x+3=9", "type":"math", "difficulty":"medium"}'
```

### Generate Hints

```bash
# Replace 1 with the actual question ID
curl -X POST "http://localhost:8000/api/v1/questions/1/hints" \
  -H "Content-Type: application/json" \
  -d '{"num_hints": 2}'
```

### Generate Solution

```bash
# Replace 1 with the actual question ID
curl -X POST "http://localhost:8000/api/v1/questions/1/solution" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Project Structure

```
motion_qna/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── static/           # Static files (CSS, JS)
│   ├── templates/        # HTML templates
│   └── main.py           # FastAPI application
├── tests/                # Unit and integration tests
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── deploy.sh             # Deployment script
└── run.py                # Application entry point
```

## Documentation

- [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) - Detailed deployment instructions
- [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) - Guide for frontend development

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the web framework
- NLTK for natural language processing
- The open-source community for various libraries used in this project 
