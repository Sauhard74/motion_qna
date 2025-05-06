import logging

from app.core.database import init_db
from app.services.ai_service import AIService


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def initialize_app():
    """Initialize the application components."""
    # Set up logging
    setup_logging()
    
    # Initialize the database
    logging.info("Initializing database...")
    init_db()
    logging.info("Database initialized")
    
    # Initialize the AI service (download models if needed)
    logging.info("Initializing AI service...")
    _ = AIService()  # This will trigger model downloads if needed
    logging.info("AI service initialized")
    
    # Log successful initialization
    logging.info("Application initialized successfully")


def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import nltk
        import transformers
        logging.info("All dependencies available")
        return True
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        return False 