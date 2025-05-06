import os
import sys
import logging
import argparse
import uvicorn

from app.core.setup import initialize_app, check_dependencies


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Motion Q&A - Question Analysis and Solution Generation API")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--no-models", action="store_true", help="Disable transformer models (use templates)")
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    # Parse arguments
    args = parse_args()
    
    # Setup environment
    if args.no_models:
        os.environ["USE_TRANSFORMERS"] = "False"
        os.environ["USE_AI_MODELS"] = "False"
    else:
        # Set default if not explicitly set
        os.environ.setdefault("USE_TRANSFORMERS", str(os.environ.get("USE_TRANSFORMERS", "True")))
        os.environ.setdefault("USE_AI_MODELS", str(os.environ.get("USE_AI_MODELS", "True")))
        
    # Check dependencies
    if not check_dependencies():
        logging.error("Failed to start: missing dependencies")
        sys.exit(1)
    
    # Initialize the application
    initialize_app()
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main() 