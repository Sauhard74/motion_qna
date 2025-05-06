from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create SQLAlchemy engine
# Ensure the database URL starts with sqlite:///
db_url = settings.DATABASE_URL
if db_url.startswith('sqlite://') and not db_url.startswith('sqlite:///'):
    db_url = 'sqlite:///' + db_url.replace('sqlite://', '')
elif not db_url.startswith('sqlite://'):
    db_url = 'sqlite:///' + db_url

engine = create_engine(
    db_url, 
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Create a new database session and ensure it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize all models at import time
def init_db() -> None:
    """Initialize the database with all models."""
    from app.models.base import Base
    Base.metadata.create_all(bind=engine) 