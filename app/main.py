from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.routes import router as discounts_router
from app.db.seed import create_tables, seed_data
from app.db.base import SessionLocal
from app.core.errors import DiscountServiceError
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed data on startup
    create_tables()
    db = SessionLocal()
    try:
        seed_data(db)
        yield
    finally:
        db.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(discounts_router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(DiscountServiceError)
async def discount_service_error_handler(_, exc: DiscountServiceError):
    return JSONResponse(status_code=400, content={"code": exc.code.value, "message": exc.message})
