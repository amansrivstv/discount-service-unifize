from decimal import Decimal
from app.services.discount_service import (
    DiscountService,
    Product,
    CartItem,
    PaymentInfo,
    CustomerProfile,
    BrandTier,
    CustomerTier,
)


def test_multiple_discount_scenario(db_session):
    service = DiscountService(db_session)

    product = Product(
        id="sku-1",
        brand="PUMA",
        brand_tier=BrandTier.REGULAR,
        category="T-shirts",
        base_price=Decimal("1000.00"),
        current_price=Decimal("1000.00"),
    )

    cart_items = [
        CartItem(product=product, quantity=1, size="M"),
    ]

    customer = CustomerProfile(id="cust-1", tier=CustomerTier.GOLD)
    payment_info = PaymentInfo(method="CARD", bank_name="ICICI", card_type="CREDIT")

    import asyncio
    discounted = asyncio.run(
        service.calculate_cart_discounts(cart_items=cart_items, customer=customer, payment_info=payment_info)
    )

    assert discounted.original_price == Decimal("1000.00")
    # Brand 40% => 600, Category 10% => 540, Bank 10% => 486
    assert discounted.final_price == Decimal("486.00")


def test_validate_voucher(db_session):
    service = DiscountService(db_session)

    product = Product(
        id="sku-2",
        brand="PUMA",
        brand_tier=BrandTier.REGULAR,
        category="T-shirts",
        base_price=Decimal("1000.00"),
        current_price=Decimal("1000.00"),
    )

    cart_items = [CartItem(product=product, quantity=1, size="L")]
    customer = CustomerProfile(id="cust-2", tier=CustomerTier.SILVER)

    import asyncio
    valid = asyncio.run(
        service.validate_discount_code(code="SUPER69", cart_items=cart_items, customer=customer)
    )

    assert valid is True
