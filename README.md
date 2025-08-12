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

### Project structure
```
app/
  api/
    routes.py
    schemas.py
  core/
    config.py
    errors.py
  db/
    base.py
    models.py
    seed.py
  services/
    discount_service.py
  fake_data.py
  main.py
requirements.txt
README.md
tests/
  conftest.py
  test_discount_service.py
```

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

- For a PUMA T-shirt priced 1000:
  - Brand 40% => 600
  - Category 10% => 540
  - Bank 10% => 486 final
