from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    DISCOUNT_CODE_INVALID = "DISCOUNT_CODE_INVALID"
    DISCOUNT_CODE_NOT_APPLICABLE = "DISCOUNT_CODE_NOT_APPLICABLE"
    BRAND_EXCLUDED = "BRAND_EXCLUDED"
    CATEGORY_RESTRICTED = "CATEGORY_RESTRICTED"
    CUSTOMER_TIER_REQUIRED = "CUSTOMER_TIER_REQUIRED"


class DiscountServiceError(Exception):
    def __init__(self, code: ErrorCode, message: Optional[str] = None):
        self.code = code
        self.message = message or code.value
        super().__init__(self.message)
