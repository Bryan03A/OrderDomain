from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.order_service import OrderService

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_order_service(db: Session = Depends(get_db)):
    return OrderService(db)