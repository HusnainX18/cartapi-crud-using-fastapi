from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from app.exceptions.custom_exceptions import (
    CartNotFoundException,
    CartItemNotFoundException,
    ProductVariantNotFoundException,
    InsufficientInventoryException,
    ItemAlreadyInCartException,
    CartNotActiveException,
    UserNotFoundException,
    EmailAlreadyExistsException,
    ProductNotFoundException,
    SkuAlreadyExistsException,
    EmptyCartException,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app):
    """
    Register all custom exception handlers onto the FastAPI app.
    This keeps main.py clean and centralises error responses.
    """

    @app.exception_handler(CartNotFoundException)
    async def cart_not_found_handler(request: Request, exc: CartNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"msg": exc.message})

    @app.exception_handler(CartItemNotFoundException)
    async def item_not_found_handler(request: Request, exc: CartItemNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"msg": exc.message})

    @app.exception_handler(ProductVariantNotFoundException)
    async def variant_not_found_handler(
        request: Request, exc: ProductVariantNotFoundException
    ):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"msg": exc.message})

    @app.exception_handler(InsufficientInventoryException)
    async def insufficient_inventory_handler(
        request: Request, exc: InsufficientInventoryException
    ):
        logger.warning(exc.message)
        return JSONResponse(status_code=422, content={"msg": exc.message})

    @app.exception_handler(ItemAlreadyInCartException)
    async def item_already_in_cart_handler(
        request: Request, exc: ItemAlreadyInCartException
    ):
        logger.warning(exc.message)
        return JSONResponse(status_code=409, content={"msg": exc.message})

    @app.exception_handler(CartNotActiveException)
    async def cart_not_active_handler(request: Request, exc: CartNotActiveException):
        logger.warning(exc.message)
        return JSONResponse(status_code=400, content={"msg": exc.message})

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"msg": exc.message})

    @app.exception_handler(EmailAlreadyExistsException)
    async def email_already_exists_handler(request: Request, exc: EmailAlreadyExistsException):
        logger.warning(exc.message)
        return JSONResponse(status_code=409, content={"msg": exc.message})

    @app.exception_handler(ProductNotFoundException)
    async def product_not_found_handler(request: Request, exc: ProductNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"msg": exc.message})

    @app.exception_handler(SkuAlreadyExistsException)
    async def sku_already_exists_handler(request: Request, exc: SkuAlreadyExistsException):
        logger.warning(exc.message)
        return JSONResponse(status_code=409, content={"msg": exc.message})

    @app.exception_handler(EmptyCartException)
    async def empty_cart_handler(request: Request, exc: EmptyCartException):
        logger.warning(exc.message)
        return JSONResponse(status_code=400, content={"msg": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if errors:
            first = errors[0]
            field = first.get("loc", [])
            field_name = field[-1] if field else "request"
            msg = f"{field_name}: {first.get('msg', 'Invalid input')}"
        else:
            msg = "Invalid request"
        logger.warning(f"Validation error: {msg}")
        return JSONResponse(status_code=422, content={"msg": msg})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, str):
            msg = detail
        else:
            msg = "Request failed"
        logger.warning(f"HTTP error {exc.status_code}: {msg}")
        return JSONResponse(status_code=exc.status_code, content={"msg": msg})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        orig = getattr(exc, "orig", exc)
        logger.error(
            f"DB IntegrityError on {request.method} {request.url.path} | {orig}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=409,
            content={
                "msg": "Database constraint failed. "
                       "The request conflicts with existing data or violates a relationship."
            },
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        orig = getattr(exc, "orig", exc)
        logger.error(
            f"DB OperationalError on {request.method} {request.url.path} | {orig}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=503,
            content={"msg": "Database is unavailable. Please try again shortly."},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error(
            f"DB SQLAlchemyError on {request.method} {request.url.path} | {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"msg": "A database error occurred. Please try again later."},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path} | "
            f"{type(exc).__name__}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"msg": "An unexpected error occurred. Please try again."},
        )
