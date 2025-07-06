from fastapi import FastAPI
from app.api.orders import router as orders_router

app = FastAPI(title="Order Status Service")

app.include_router(orders_router)

# FastAPI recommends running via: `uvicorn app.main:app --host 0.0.0.0 --port 5017`