from sqlalchemy.orm import Session
from app.db.base import Base, engine
from app.db import models
from app.fake_data import BRAND_DISCOUNTS, CATEGORY_DISCOUNTS, BANK_OFFERS, VOUCHERS


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_data(db: Session) -> None:
    # Seed brand discounts
    for bd in BRAND_DISCOUNTS:
        existing = db.query(models.BrandDiscount).filter_by(brand=bd["brand"]).one_or_none()
        if not existing:
            db.add(models.BrandDiscount(**bd))

    # Seed category discounts
    for cd in CATEGORY_DISCOUNTS:
        existing = db.query(models.CategoryDiscount).filter_by(category=cd["category"]).one_or_none()
        if not existing:
            db.add(models.CategoryDiscount(**cd))

    # Seed bank offers
    for bo in BANK_OFFERS:
        existing = (
            db.query(models.BankOffer)
            .filter_by(bank_name=bo["bank_name"], payment_method=bo["payment_method"], card_type=bo.get("card_type"))
            .one_or_none()
        )
        if not existing:
            db.add(models.BankOffer(**bo))

    # Seed vouchers
    for v in VOUCHERS:
        existing = db.query(models.Voucher).filter_by(code=v["code"]).one_or_none()
        if not existing:
            db.add(models.Voucher(**v))

    db.commit()
