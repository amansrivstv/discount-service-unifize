from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal
from enum import Enum


class BrandTier(str, Enum):
    PREMIUM = "premium"
    REGULAR = "regular"
    BUDGET = "budget"


class CustomerTier(str, Enum):
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"


class Product(BaseModel):
    id: str
    brand: str
    brand_tier: BrandTier
    category: str
    base_price: Decimal
    current_price: Decimal = Field(..., description="Price after brand/category discounts")


class CartItem(BaseModel):
    product: Product
    quantity: int
    size: str


class PaymentInfo(BaseModel):
    method: str
    bank_name: Optional[str] = None
    card_type: Optional[str] = None


class CustomerProfile(BaseModel):
    id: str
    tier: CustomerTier


class DiscountedPrice(BaseModel):
    original_price: Decimal
    final_price: Decimal
    applied_discounts: Dict[str, Decimal]
    message: str


class CalculateRequest(BaseModel):
    cart_items: List[CartItem]
    customer: CustomerProfile
    payment_info: Optional[PaymentInfo] = None
    voucher_code: Optional[str] = None


class ValidateCodeRequest(BaseModel):
    code: str
    cart_items: List[CartItem]
    customer: CustomerProfile


class ValidateCodeResponse(BaseModel):
    valid: bool
