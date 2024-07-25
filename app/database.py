import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

log = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

log.info(f"Initializing database connection with URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    log.info("Database engine created successfully")
except Exception as e:
    log.exception(f"Error creating database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
log.info("SessionLocal created")

Base = declarative_base()
log.info("Declarative base created")

def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for dependency injection.

    Yields:
        Generator[Session, None, None]: The database session.
    """
    db = SessionLocal()
    log.info("New database session created")
    try:
        yield db
    finally:
        log.info("Closing database session")
        db.close()

log.info("Database setup completed")