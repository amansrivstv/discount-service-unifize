from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router as discounts_router
from app.db.seed import create_tables, seed_data
from app.db.base import SessionLocal

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

app = FastAPI(title="Discount Service", lifespan=lifespan)
app.include_router(discounts_router)

@app.get("/health")
def health():
    return {"status": "ok"}
