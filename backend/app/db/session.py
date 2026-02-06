"""Database engine, session factory, and session context manager."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@contextmanager
def get_db():
    """
    Provides a transactional scope around a series of operations.
    """
    db = SessionLocal()
    try:
        try:
            yield db
        except Exception:
            db.rollback()
            raise
    finally:
        db.close()
