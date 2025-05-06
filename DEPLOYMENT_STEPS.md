# Motion Q&A: Deployment Steps

This document outlines the steps taken to deploy the Motion Q&A application.

## 1. Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/motion_qna.git
   cd motion_qna
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install NLTK resources**:
   ```bash
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
   ```

## 2. Local Deployment

1. **Initialize the database**:
   ```bash
   python -c "from app.core.setup import initialize_app; initialize_app()"
   ```

2. **Run the application locally**:
   ```bash
   python run.py --host localhost --port 8000
   ```

3. **Use template-based generation (without heavy ML models)**:
   ```bash
   python run.py --host localhost --port 8000 --no-models
   ```

## 3. Docker Deployment

1. **Create a .dockerignore file**:
   ```
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   env/
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   *.egg-info/
   .installed.cfg
   *.egg

   # Virtual Environment
   venv/
   ENV/
   env/

   # Git
   .git
   .gitignore

   # Project specific
   motion_qna.db
   *.log
   .DS_Store
   .env.local
   .env.development.local
   .env.test.local
   .env.production.local
   ```

2. **Create or update the Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   # Set environment variables
   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1
   ENV USE_TRANSFORMERS=False
   ENV USE_AI_MODELS=False

   # Install dependencies in stages
   # First install only essential packages
   COPY requirements-minimal.txt .
   RUN pip install --no-cache-dir -r requirements-minimal.txt

   # Then install NLTK packages
   RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

   # Copy project
   COPY . .

   # Create a shell script to initialize the database and start the server
   RUN echo '#!/bin/sh\npython -c "from app.core.setup import initialize_app; initialize_app()"\nuvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/startup.sh
   RUN chmod +x /app/startup.sh

   # Expose port
   EXPOSE 8000

   # Initialize database and run application
   CMD ["/app/startup.sh"]
   ```

3. **Build the Docker image**:
   ```bash
   docker build -t motion_qna:latest .
   ```

4. **Run the Docker container**:
   ```bash
   docker run -d -p 8000:8000 --name motion_qna_app motion_qna:latest
   ```

5. **Verify the application is running**:
   ```bash
   curl http://localhost:8000/
   ```

6. **Test the API endpoints**:
   ```bash
   # Submit a question
   curl -X POST "http://localhost:8000/api/v1/questions/" -H "Content-Type: application/json" -d '{"content":"solve x: x+3=9", "type":"math", "difficulty":"medium"}'
   
   # Generate hints for the question (replace 1 with the actual question ID)
   curl -X POST "http://localhost:8000/api/v1/questions/1/hints" -H "Content-Type: application/json" -d '{"num_hints": 2}'
   
   # Generate solution for the question (replace 1 with the actual question ID)
   curl -X POST "http://localhost:8000/api/v1/questions/1/solution" -H "Content-Type: application/json" -d '{}'
   ```

## 4. Cloud Deployment

### Heroku Deployment

1. **Create a Heroku account and install the Heroku CLI**

2. **Log in to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

4. **Add a Procfile** (already in the project):
   ```
   web: python -c "from app.core.setup import initialize_app; initialize_app()" && uvicorn app.main:app --host=0.0.0.0 --port=$PORT
   ```

5. **Deploy to Heroku**:
   ```bash
   git push heroku main
   ```

### AWS Deployment

1. **Create an EC2 instance**

2. **Install Docker on the EC2 instance**:
   ```bash
   sudo yum update -y
   sudo amazon-linux-extras install docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```

3. **Clone the repository on EC2**:
   ```bash
   git clone https://github.com/yourusername/motion_qna.git
   cd motion_qna
   ```

4. **Build and run with Docker**:
   ```bash
   docker build -t motion_qna .
   docker run -d -p 8000:8000 motion_qna
   ```

5. **Configure security groups to allow traffic on port 8000**

## 5. Maintenance and Monitoring

1. **View Docker logs**:
   ```bash
   docker logs motion_qna_app
   ```

2. **Stop the Docker container**:
   ```bash
   docker stop motion_qna_app
   ```

3. **Restart the Docker container**:
   ```bash
   docker start motion_qna_app
   ```

4. **Update the application**:
   ```bash
   git pull
   docker build -t motion_qna:latest .
   docker stop motion_qna_app
   docker rm motion_qna_app
   docker run -d -p 8000:8000 --name motion_qna_app motion_qna:latest
   ```

## 6. Troubleshooting

1. **NLTK resource errors**: Install the required NLTK packages
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

2. **Version compatibility issues**: Use the Docker deployment to avoid dependency conflicts

3. **Database initialization issues**: Make sure to initialize the database before starting the application
   ```bash
   python -c "from app.core.setup import initialize_app; initialize_app()"
   ```

4. **Disk space issues**: Clean up Docker resources
   ```bash
   docker system prune -af
   ```

5. **Port conflicts**: Change the port or check for processes using the same port
   ```bash
   docker run -d -p 8001:8000 --name motion_qna_app motion_qna:latest
   ```

6. **HTTP 500 errors**: Check the Docker logs for specific error messages
   ```bash
   docker logs motion_qna_app
   ``` 