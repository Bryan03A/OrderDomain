from sqlalchemy.orm import Session
from app.models import Order

class OrderRepository:
    """Performs CRUD operations on Order."""

    def __init__(self, db: Session):
        self.db = db

    # ----- Reading -----
    def get_by_order_id(self, order_id: int) -> Order | None:
        return (self.db.query(Order)
                .filter(Order.order_id == order_id)
                .first())

    # ----- Writing -----
    def add(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def save(self, order: Order) -> Order:
        self.db.commit()
        self.db.refresh(order)
        return order