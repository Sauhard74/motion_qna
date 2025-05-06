# Motion Q&A Deployment Guide

This guide provides comprehensive instructions for deploying the Motion Q&A system in various environments.

## Prerequisites

- Python 3.1+
- Git
- Docker (optional, for containerized deployment)
- Basic understanding of web application deployment

## Local Deployment

### Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/Sauhard74/motion_qna.git
cd motion_qna
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install required NLTK packages:
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

5. Run the application:
```bash
python run.py --host localhost --port 8000
```

6. Access the application at http://localhost:8000

### Configuration Options

The application can be configured using command-line arguments:

- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development
- `--no-models`: Disable transformer models (use templates)

Example:
```bash
python run.py --host localhost --port 8000 --reload
```

### Environment Variables

The application can be configured using the following environment variables:

- `USE_TRANSFORMERS`: Set to "False" to disable transformer models
- `USE_AI_MODELS`: Set to "False" to disable AI model-based generation
- `DATABASE_URL`: Database connection string (default: sqlite:///motion_qna.db)

Example:
```bash
export USE_TRANSFORMERS=False
export USE_AI_MODELS=False
python run.py
```

## Docker Deployment

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/yourusername/motion_qna.git
cd motion_qna
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. Access the application at http://localhost:8000

### Using Docker Directly

1. Clone the repository:
```bash
git clone https://github.com/yourusername/motion_qna.git
cd motion_qna
```

2. Build the Docker image:
```bash
docker build -t motion_qna .
```

3. Run the container:
```bash
docker run -d -p 8000:8000 --name motion_qna_app motion_qna
```

4. Access the application at http://localhost:8000

## Cloud Deployment

### Heroku Deployment

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku and create a new app:
```bash
heroku login
heroku create your-app-name
```

3. Add the Procfile (already included in the repository):
```
web: uvicorn app.main:app --host=0.0.0.0 --port=$PORT
```

4. Add Heroku PostgreSQL (optional, if you want to use PostgreSQL instead of SQLite):
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

5. Push to Heroku:
```bash
git push heroku main
```

6. Open the application:
```bash
heroku open
```

### AWS Deployment

#### EC2 Instance with Docker

1. Launch an EC2 instance with Amazon Linux 2
2. SSH into the instance
3. Install Docker and Docker Compose:
```bash
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/download/v2.16.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

4. Clone the repository and deploy:
```bash
git clone https://github.com/yourusername/motion_qna.git
cd motion_qna
docker-compose up -d
```

5. Configure security groups to allow traffic on port 8000

#### AWS ECS with Fargate

1. Create an ECR repository:
```bash
aws ecr create-repository --repository-name motion-qna
```

2. Build, tag, and push the Docker image:
```bash
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
docker build -t motion_qna .
docker tag motion_qna:latest aws_account_id.dkr.ecr.region.amazonaws.com/motion-qna:latest
docker push aws_account_id.dkr.ecr.region.amazonaws.com/motion-qna:latest
```

3. Create an ECS cluster, task definition, and service through the AWS console or CLI

### Google Cloud Platform (GCP) Deployment

#### Cloud Run

1. Install and configure the Google Cloud SDK
2. Build and push the Docker image to Google Container Registry:
```bash
gcloud builds submit --tag gcr.io/project-id/motion-qna
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy motion-qna --image gcr.io/project-id/motion-qna --platform managed --region us-central1 --allow-unauthenticated
```

## Performance Optimization

### Resource-Limited Environments

For environments with limited resources, use the minimal requirements and disable transformer models:

```bash
pip install -r requirements-minimal.txt
export USE_TRANSFORMERS=False
export USE_AI_MODELS=False
python run.py
```

### High-Performance Environments

For high-performance environments, ensure you have sufficient RAM (at least 8GB) and consider using GPU-accelerated instances if available. Set environment variables accordingly:

```bash
export USE_TRANSFORMERS=True
export USE_AI_MODELS=True
python run.py
```

## Monitoring and Maintenance

### Logs

Application logs are output to the console and can be redirected to a file:

```bash
python run.py > application.log 2>&1
```

In Docker, logs can be viewed with:

```bash
docker logs motion_qna_app
```

### Database Backup

To backup the SQLite database:

```bash
sqlite3 motion_qna.db .dump > backup.sql
```

### Updating the Application

1. Pull the latest changes:
```bash
git pull origin main
```

2. Restart the application or rebuild Docker containers:
```bash
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **NLTK Resource Errors**:
   - Run `python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"`

2. **Model Loading Errors**:
   - Ensure you have enough RAM or use `--no-models` flag
   - Check disk space requirements

3. **Database Connection Errors**:
   - Verify database path and permissions

4. **Port Already in Use**:
   - Change the port using `--port` option
   - Check for running processes using the same port 