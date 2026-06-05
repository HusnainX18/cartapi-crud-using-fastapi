from fastapi import Request
from fastapi.responses import JSONResponse
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
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(CartItemNotFoundException)
    async def item_not_found_handler(request: Request, exc: CartItemNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(ProductVariantNotFoundException)
    async def variant_not_found_handler(
        request: Request, exc: ProductVariantNotFoundException
    ):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(InsufficientInventoryException)
    async def insufficient_inventory_handler(
        request: Request, exc: InsufficientInventoryException
    ):
        logger.warning(exc.message)
        return JSONResponse(status_code=422, content={"detail": exc.message})

    @app.exception_handler(ItemAlreadyInCartException)
    async def item_already_in_cart_handler(
        request: Request, exc: ItemAlreadyInCartException
    ):
        logger.warning(exc.message)
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(CartNotActiveException)
    async def cart_not_active_handler(request: Request, exc: CartNotActiveException):
        logger.warning(exc.message)
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(EmailAlreadyExistsException)
    async def email_already_exists_handler(request: Request, exc: EmailAlreadyExistsException):
        logger.warning(exc.message)
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(ProductNotFoundException)
    async def product_not_found_handler(request: Request, exc: ProductNotFoundException):
        logger.warning(exc.message)
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(SkuAlreadyExistsException)
    async def sku_already_exists_handler(request: Request, exc: SkuAlreadyExistsException):
        logger.warning(exc.message)
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again."},
        )