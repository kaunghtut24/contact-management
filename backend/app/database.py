from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings

engine = None

# Production environment (Vercel with Neon - PostgreSQL)
# Use NullPool for serverless compatibility, as each function invocation might get a new container.
if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True
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