from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.db.base import Base


class CardType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class BrandDiscount(Base):
    __tablename__ = "brand_discounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String, index=True, nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 40 for 40%

    __table_args__ = (
        UniqueConstraint("brand", name="uq_brand"),
    )


class CategoryDiscount(Base):
    __tablename__ = "category_discounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String, index=True, nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("category", name="uq_category"),
    )


class BankOffer(Base):
    __tablename__ = "bank_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bank_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    payment_method: Mapped[str] = mapped_column(String, nullable=False)  # CARD, UPI, etc.
    card_type: Mapped[str | None] = mapped_column(String, nullable=True)  # CREDIT, DEBIT
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)


class Voucher(Base):
    __tablename__ = "vouchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    # Optional constraints
    excluded_brands: Mapped[str | None] = mapped_column(String, nullable=True)  # CSV
    allowed_categories: Mapped[str | None] = mapped_column(String, nullable=True)  # CSV
    required_customer_tier: Mapped[str | None] = mapped_column(String, nullable=True)
