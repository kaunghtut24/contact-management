from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

Base = declarative_base()

engine = None

# Production environment (PostgreSQL - Neon/Render)
if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,  # For serverless compatibility
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require"
        }
    )
# Development environment (local with SQLite)
elif settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
# Fallback for other database types if needed
else:
    engine = create_engine(settings.DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency that provides a database session to the API endpoints.
    This function ensures that the database session is always closed
    after the request has been handled, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()