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

# Expose port
EXPOSE 8000

# Create a shell script to initialize the database and start the server
RUN echo '#!/bin/sh\npython -c "from app.core.setup import initialize_app; initialize_app()"\nuvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/startup.sh
RUN chmod +x /app/startup.sh

# Initialize database and run application
CMD ["/app/startup.sh"] 