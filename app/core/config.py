from pydantic import BaseModel
import os


class Settings(BaseModel):
    sqlite_url: str = os.getenv("DISCOUNT_DB_URL", "sqlite:///./discounts.db")
    app_name: str = "Discount Service"


settings = Settings()
