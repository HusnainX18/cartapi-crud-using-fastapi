from unittest.mock import MagicMock

import pytest

from app.constants.status import CartStatus
from app.exceptions.custom_exceptions import InsufficientInventoryException
from app.services.cart_service import CartService
from tests.factories import ProductVariantFactory


def test_checkout_raises_if_insufficient_inventory():
    # 1. Arrange: Create mock DB session and cart repository
    mock_db = MagicMock()
    mock_cart_repo = MagicMock()

    # 2. Setup mock objects using factory_boy
    fake_variant = ProductVariantFactory(inventory_qty=5)

    mock_item = MagicMock()
    mock_item.product_variant_id = fake_variant.id
    mock_item.quantity = 10  # Order qty (10) > stock (5)
    mock_item.variant = fake_variant

    mock_cart = MagicMock()
    mock_cart.status = CartStatus.ACTIVE
    mock_cart.items = [mock_item]

    mock_cart_repo.get_cart_by_id.return_value = mock_cart
    mock_cart_repo.get_variant_by_id.return_value = fake_variant

    # Instantiate service injecting mock repo
    service = CartService(db=mock_db)
    service.repo = mock_cart_repo

    # 3. Act & Assert: Checkout must raise InsufficientInventoryException
    with pytest.raises(InsufficientInventoryException):
        service.checkout(cart_id=1)
