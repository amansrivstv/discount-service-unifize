from fastapi import APIRouter, Depends, Body
from fastapi import status
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


@router.post(
    "/calculate",
    response_model=DiscountedPriceSchema,
    responses={
        200: {
            "description": "Discounts calculated",
            "content": {
                "application/json": {
                    "example": {
                        "original_price": 1000.0,
                        "final_price": 486.0,
                        "applied_discounts": {
                            "brand:PUMA:40%": 400.0,
                            "category:T-shirts:10%": 60.0,
                            "bank:ICICI:10%": 54.0,
                        },
                        "message": "Discounts applied successfully",
                    }
                }
            },
        }
    },
)
async def calculate_discounts(
    payload: CalculateRequest = Body(
        ...,
        example={
            "cart_items": [
                {
                    "product": {
                        "id": "sku-1",
                        "brand": "PUMA",
                        "brand_tier": "regular",
                        "category": "T-shirts",
                        "base_price": 1000.0,
                        "current_price": 1000.0,
                    },
                    "quantity": 1,
                    "size": "M",
                }
            ],
            "customer": {"id": "cust-1", "tier": "gold"},
            "payment_info": {"method": "CARD", "bank_name": "ICICI", "card_type": "CREDIT"},
            "voucher_code": "SUPER69",
        },
    ),
    db: Session = Depends(get_db_session),
):
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
        voucher_code=payload.voucher_code,
    )
    return DiscountedPriceSchema(
        original_price=result.original_price,
        final_price=result.final_price,
        applied_discounts=result.applied_discounts,
        message=result.message,
    )


@router.post(
    "/validate-code",
    response_model=ValidateCodeResponse,
    responses={
        200: {
            "description": "Code valid",
            "content": {"application/json": {"example": {"valid": True}}},
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_code": {
                            "summary": "Invalid code",
                            "value": {"code": "DISCOUNT_CODE_INVALID", "message": "Discount code does not exist"},
                        },
                        "brand_excluded": {
                            "summary": "Brand excluded",
                            "value": {"code": "BRAND_EXCLUDED", "message": "Brand PUMA is excluded for this voucher"},
                        },
                        "category_restricted": {
                            "summary": "Category restricted",
                            "value": {"code": "CATEGORY_RESTRICTED", "message": "Category T-shirts not eligible"},
                        },
                        "customer_tier_required": {
                            "summary": "Customer tier not eligible",
                            "value": {"code": "CUSTOMER_TIER_REQUIRED", "message": "Customer tier not eligible for this voucher"},
                        },
                    }
                }
            },
        },
    },
)
async def validate_code(
    payload: ValidateCodeRequest = Body(
        ...,
        example={
            "code": "SUPER69",
            "cart_items": [
                {
                    "product": {
                        "id": "sku-3",
                        "brand": "PUMA",
                        "brand_tier": "regular",
                        "category": "T-shirts",
                        "base_price": 1000.0,
                        "current_price": 1000.0,
                    },
                    "quantity": 1,
                    "size": "M",
                }
            ],
            "customer": {"id": "cust-3", "tier": "silver"},
        },
    ),
    db: Session = Depends(get_db_session),
):
    service = DiscountService(db)
    valid = await service.validate_discount_code(
        code=payload.code,
        cart_items=map_cart_items(payload.cart_items),
        customer=DCustomerProfile(id=payload.customer.id, tier=payload.customer.tier),
    )
    return ValidateCodeResponse(valid=valid)
