from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import get_logger
from app.db.database import Base, engine
from app.middleware.logging_middleware import LoggingMiddleware
from app.exceptions.handlers import register_exception_handlers
from app.api.v1.cart_router import router as cart_router
from app.api.v1.user_router import router as user_router
from app.api.v1.product_router import router as product_router
from app.schemas.response import MessageResponse

# Must import models so Base knows about them before create_all
import app.models  # noqa: F401

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-style Cart CRUD API built with FastAPI + SQLAlchemy",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware
    app.add_middleware(LoggingMiddleware)

    # Exception handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(cart_router, prefix="/api/v1")
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(product_router, prefix="/api/v1")

    # Create tables if they don't exist (fine for dev — use Alembic for prod)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")

    @app.get("/", tags=["Health"], response_model=MessageResponse)
    def health_check():
        return MessageResponse(msg=f"{settings.APP_NAME} v{settings.APP_VERSION} is up")

    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started")
    return app


app = create_app()
