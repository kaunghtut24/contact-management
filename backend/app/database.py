from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine with production-ready settings
if settings.DATABASE_URL.startswith("sqlite"):
    # Development mode
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
elif settings.DATABASE_URL.startswith("mysql"):
    # Production mode (PlanetScale)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "charset": "utf8mb4",
            "ssl_disabled": False
        }
    )
else:
    # Other databases (PostgreSQL, etc.)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()