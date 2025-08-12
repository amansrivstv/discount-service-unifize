from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api.schemas import (
    CalculateRequest,
    DiscountedPrice as DiscountedPriceSchema,
    ValidateCodeRequest,
    ValidateCodeResponse,
)
from app.db.base import get_db_session
from app.services.discount_service import (
    DiscountService,
    CartItem as DCartItem,
    CustomerProfile as DCustomerProfile,
    PaymentInfo as DPaymentInfo,
    Product as DProduct,
)

router = APIRouter(prefix="/discounts", tags=["discounts"])


def map_cart_items(items):
    mapped = []
    for item in items:
        p = item.product
        dp = DProduct(
            id=p.id,
            brand=p.brand,
            brand_tier=p.brand_tier,
            category=p.category,
            base_price=Decimal(str(p.base_price)),
            current_price=Decimal(str(p.current_price)),
        )
        mapped.append(DCartItem(product=dp, quantity=item.quantity, size=item.size))
    return mapped


@router.post("/calculate", response_model=DiscountedPriceSchema)
async def calculate_discounts(payload: CalculateRequest, db: Session = Depends(get_db_session)):
    service = DiscountService(db)
    result = await service.calculate_cart_discounts(
        cart_items=map_cart_items(payload.cart_items),
        customer=DCustomerProfile(id=payload.customer.id, tier=payload.customer.tier),
        payment_info=(
            DPaymentInfo(
                method=payload.payment_info.method,
                bank_name=payload.payment_info.bank_name,
                card_type=payload.payment_info.card_type,
            )
            if payload.payment_info
            else None
        ),
    )
    return DiscountedPriceSchema(
        original_price=result.original_price,
        final_price=result.final_price,
        applied_discounts=result.applied_discounts,
        message=result.message,
    )


@router.post("/validate-code", response_model=ValidateCodeResponse)
async def validate_code(payload: ValidateCodeRequest, db: Session = Depends(get_db_session)):
    service = DiscountService(db)
    valid = await service.validate_discount_code(
        code=payload.code,
        cart_items=map_cart_items(payload.cart_items),
        customer=DCustomerProfile(id=payload.customer.id, tier=payload.customer.tier),
    )
    return ValidateCodeResponse(valid=valid)
