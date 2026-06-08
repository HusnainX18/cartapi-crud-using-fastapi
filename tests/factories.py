import factory

from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    email = factory.Faker("email")
    password_hash = factory.Faker("sha256")


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    brand = factory.Faker("company")


class ProductVariantFactory(factory.Factory):
    class Meta:
        model = ProductVariant

    id = factory.Sequence(lambda n: n + 1)
    product_id = factory.SelfAttribute("product.id")
    sku = factory.Sequence(lambda n: f"SKU-{n:04d}")
    price = 9.99
    currency = "USD"
    inventory_qty = 100
    product = factory.SubFactory(ProductFactory)
