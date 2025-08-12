## Discount Service

A FastAPI-based discount service using SQLite, SQLAlchemy, Pydantic, and pytest. Implements brand/category discounts, bank offers, and voucher validation.

### Features
- Brand and category discounts (brand first, then category)
- Bank offers applied on the discounted cart subtotal
- Voucher validation with brand/category/tier constraints
- SQLite storage with seed data
- API endpoints for calculation and code validation

### Tech
- FastAPI, SQLAlchemy, Pydantic, SQLite, pytest

### Project structure (current)
```
.
├── Dockerfile
├── Makefile
├── README.md
├── requirements.txt
├── .dockerignore
├── .gitignore
├── pytest.ini
├── app/
│   ├── main.py
│   ├── fake_data.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── core/
│   │   ├── cache.py
│   │   ├── config.py
│   │   └── errors.py
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py
│   │   └── seed.py
│   └── services/
│       └── discount_service.py
└── tests/
    ├── conftest.py
    └── test_discount_service.py
```

### Architecture

- **Framework and lifecycle**
  - `app/main.py` defines the FastAPI app and uses a lifespan context (not deprecated `on_event`) to:
    - create tables (`app/db/seed.py:create_tables`)
    - seed initial data (`seed_data`) on startup
  - Centralized error handling translates `DiscountServiceError` into HTTP 400 with `{code, message}`.

- **API layer** (`app/api`)
  - `routes.py`: two endpoints
    - `POST /discounts/calculate` → computes final price
    - `POST /discounts/validate-code` → validates voucher
  - Swagger/OpenAPI
    - Request examples are prefilled via `Body(example=...)` so Swagger shows a complete payload by default
    - Response examples (success and error) are defined for quick testing
  - `schemas.py`: Pydantic models for request/response (product, cart item, customer, payment info, etc.)

- **Service layer** (`app/services/discount_service.py`)
  - Single entry point: `DiscountService.calculate_cart_discounts(...)` implementing the sequence:
    1. Apply brand discount per item
    2. Apply category discount per item
    3. Apply voucher on the discounted subtotal (optional `voucher_code`)
    4. Apply bank offers on the amount after voucher
  - Uses `Decimal` for currency and `ROUND_HALF_UP` to 2 decimals
  - Returns a `DiscountedPrice` containing `original_price`, `final_price`, and a map of `applied_discounts`
  - Voucher validation via `validate_discount_code(...)` enforces brand/category/tier rules
  - Caching (`app/core/cache.py`):
    - 5‑minute TTL cache for brand/category maps, bank offers per `(bank_name, method)`, and voucher by code
    - Reduces DB hits; cache is TTL-based (no write-through invalidation)

- **Data layer** (`app/db`)
  - `base.py`: SQLAlchemy `Base`, engine, `SessionLocal` configured from `settings.sqlite_url`
  - `models.py`: tables for `BrandDiscount`, `CategoryDiscount`, `BankOffer`, `Voucher`
  - `seed.py`: creates tables and loads `app/fake_data.py`
  - Default DB: SQLite file (overridable via env `DISCOUNT_DB_URL`)

- **Core utilities** (`app/core`)
  - `config.py`: `Settings` with `app_name` and `sqlite_url` sourced from env (`DISCOUNT_DB_URL`)
  - `errors.py`: domain error codes and `DiscountServiceError`
  - `cache.py`: thread-safe simple TTL cache

- **Tests** (`tests`)
  - Use in-memory SQLite; seed representative data
  - Validates discount order and amounts (with/without voucher) and voucher validation

### Discount logic details

- Per item: brand discount is applied first, then category discount on the result.
- Cart-level: optional voucher applies a percentage on the subtotal after item discounts.
- Finally: bank offer applies a percentage on the subtotal after voucher.
- All monetary results are quantized to 2 decimals using `ROUND_HALF_UP`.

### Setup

1) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Run the API server
```bash
uvicorn app.main:app --reload
```
- Open `http://127.0.0.1:8000/docs` for Swagger UI

4) Run tests
```bash
pytest -q
```

### Makefile shortcuts

Common tasks:
```bash
# create venv and install deps
make venv install

# run service
make run

# run service in dev with reload
make dev

# run tests
make test
```

### Docker

Build and run the service using Docker:
```bash
# build image
make docker-build

# run container (exposes 8000)
make docker-run
# open http://127.0.0.1:8000/docs

# run tests inside the container
make docker-test
```

### Example
- Seeded data:
  - PUMA brand 40% off
  - T-shirts category extra 10% off
  - ICICI Credit Card 10% instant discount
  - Voucher SUPER69 (69% off) example
