# Example fake data used for seeding and tests

BRAND_DISCOUNTS = [
    {"brand": "PUMA", "discount_percent": 40},
]

CATEGORY_DISCOUNTS = [
    {"category": "T-shirts", "discount_percent": 10},
]

BANK_OFFERS = [
    {"bank_name": "ICICI", "payment_method": "CARD", "card_type": "CREDIT", "discount_percent": 10},
]

VOUCHERS = [
    {"code": "SUPER69", "discount_percent": 69, "excluded_brands": None, "allowed_categories": None, "required_customer_tier": None},
]
