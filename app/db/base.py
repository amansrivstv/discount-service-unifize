from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings


Base = declarative_base()

# Using check_same_thread=False for SQLite to allow usage across threads in FastAPI
engine = create_engine(settings.sqlite_url, connect_args={"check_same_thread": False} if settings.sqlite_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
