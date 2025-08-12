from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.errors import DiscountServiceError, ErrorCode
from app.db.models import BankOffer, BrandDiscount, CategoryDiscount, Voucher


class BrandTier(str, Enum):
    PREMIUM = "premium"
    REGULAR = "regular"
    BUDGET = "budget"


class CustomerTier(str, Enum):
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"


@dataclass
class Product:
    id: str
    brand: str
    brand_tier: BrandTier
    category: str
    base_price: Decimal
    current_price: Decimal


@dataclass
class CartItem:
    product: Product
    quantity: int
    size: str


@dataclass
class PaymentInfo:
    method: str  # CARD, UPI, etc
    bank_name: Optional[str]
    card_type: Optional[str]  # CREDIT, DEBIT


@dataclass
class DiscountedPrice:
    original_price: Decimal
    final_price: Decimal
    applied_discounts: Dict[str, Decimal]
    message: str


@dataclass
class CustomerProfile:
    id: str
    tier: CustomerTier


def _to_decimal(value: float | int | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _apply_percent(amount: Decimal, percent: int) -> Decimal:
    discount = (amount * Decimal(percent) / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return discount


class DiscountService:
    def __init__(self, db: Session):
        self.db = db

    async def calculate_cart_discounts(
        self,
        cart_items: List[CartItem],
        customer: CustomerProfile,
        payment_info: Optional[PaymentInfo] = None,
    ) -> DiscountedPrice:
        """
        Calculate final price after applying discount logic:
        - First apply brand/category discounts
        - Then apply coupon codes (not auto-applied here)
        - Then apply bank offers
        """
        original_total = Decimal("0.00")
        subtotal_after_item_discounts = Decimal("0.00")
        applied: Dict[str, Decimal] = {}

        # Preload discounts
        brand_discounts: Dict[str, int] = {bd.brand.lower(): bd.discount_percent for bd in self.db.query(BrandDiscount).all()}
        category_discounts: Dict[str, int] = {cd.category.lower(): cd.discount_percent for cd in self.db.query(CategoryDiscount).all()}

        for item in cart_items:
            unit_price = _to_decimal(item.product.base_price)
            original_total += (unit_price * item.quantity)

            # Brand discount first
            brand_percent = brand_discounts.get(item.product.brand.lower(), 0)
            brand_discount_amount = _apply_percent(unit_price, brand_percent) if brand_percent else Decimal("0.00")
            price_after_brand = unit_price - brand_discount_amount

            if brand_percent:
                applied_key = f"brand:{item.product.brand}:{brand_percent}%"
                applied[applied_key] = applied.get(applied_key, Decimal("0.00")) + (brand_discount_amount * item.quantity)

            # Category discount next
            category_percent = category_discounts.get(item.product.category.lower(), 0)
            category_discount_amount = _apply_percent(price_after_brand, category_percent) if category_percent else Decimal("0.00")
            final_unit_price = price_after_brand - category_discount_amount

            if category_percent:
                applied_key = f"category:{item.product.category}:{category_percent}%"
                applied[applied_key] = applied.get(applied_key, Decimal("0.00")) + (category_discount_amount * item.quantity)

            # Update product current price for transparency
            item.product.current_price = final_unit_price

            subtotal_after_item_discounts += (final_unit_price * item.quantity)

        # Bank offer on subtotal
        bank_discount_total = Decimal("0.00")
        if payment_info and payment_info.bank_name:
            offers = (
                self.db.query(BankOffer)
                .filter(
                    BankOffer.bank_name == payment_info.bank_name,
                    BankOffer.payment_method == payment_info.method,
                )
                .all()
            )
            for offer in offers:
                if offer.card_type and payment_info.card_type and (offer.card_type.upper() != payment_info.card_type.upper()):
                    continue
                discount_amount = _apply_percent(subtotal_after_item_discounts, offer.discount_percent)
                bank_discount_total += discount_amount
                applied_key = f"bank:{offer.bank_name}:{offer.discount_percent}%"
                applied[applied_key] = applied.get(applied_key, Decimal("0.00")) + discount_amount

        final_total = (subtotal_after_item_discounts - bank_discount_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return DiscountedPrice(
            original_price=original_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            final_price=final_total,
            applied_discounts={k: v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) for k, v in applied.items()},
            message="Discounts applied successfully",
        )

    async def validate_discount_code(
        self,
        code: str,
        cart_items: List[CartItem],
        customer: CustomerProfile,
    ) -> bool:
        voucher: Voucher | None = self.db.query(Voucher).filter(Voucher.code == code).one_or_none()
        if not voucher:
            raise DiscountServiceError(ErrorCode.DISCOUNT_CODE_INVALID, "Discount code does not exist")

        # Check brand exclusions
        excluded_brands = [b.strip().lower() for b in (voucher.excluded_brands or "").split(",") if b.strip()]
        if excluded_brands:
            for item in cart_items:
                if item.product.brand.lower() in excluded_brands:
                    raise DiscountServiceError(ErrorCode.BRAND_EXCLUDED, f"Brand {item.product.brand} is excluded for this voucher")

        # Check allowed categories
        allowed_categories = [c.strip().lower() for c in (voucher.allowed_categories or "").split(",") if c.strip()]
        if allowed_categories:
            for item in cart_items:
                if item.product.category.lower() not in allowed_categories:
                    raise DiscountServiceError(ErrorCode.CATEGORY_RESTRICTED, f"Category {item.product.category} not eligible")

        # Check customer tier requirement
        if voucher.required_customer_tier and voucher.required_customer_tier.lower() != customer.tier.value.lower():
            raise DiscountServiceError(ErrorCode.CUSTOMER_TIER_REQUIRED, "Customer tier not eligible for this voucher")

        return True
