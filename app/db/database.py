from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Checks connection health before use
    pool_size=10,  # Max connections in pool
    max_overflow=20,  # Extra connections beyond pool_size
    echo=settings.DEBUG,  # Logs all SQL when DEBUG=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency Injection — FastAPI injects this into every route.
    Rolls back the session if any exception is raised during the request,
    and always closes it at the end.
    """
    db = SessionLocal()
    try:
        logger.debug("DB session opened")
        yield db
    except Exception as e:
        db.rollback()
        logger.warning(f"DB session rolled back due to {type(e).__name__}: {e}")
        raise
    finally:
        db.close()
        logger.debug("DB session closed")
