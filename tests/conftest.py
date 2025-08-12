import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db import models
from app.fake_data import BRAND_DISCOUNTS, CATEGORY_DISCOUNTS, BANK_OFFERS, VOUCHERS


@pytest.fixture()
def db_session():
    # In-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    # Manual seed using fake data
    for bd in BRAND_DISCOUNTS:
        session.add(models.BrandDiscount(**bd))
    for cd in CATEGORY_DISCOUNTS:
        session.add(models.CategoryDiscount(**cd))
    for bo in BANK_OFFERS:
        session.add(models.BankOffer(**bo))
    for v in VOUCHERS:
        session.add(models.Voucher(**v))

    session.commit()

    try:
        yield session
    finally:
        session.close()
