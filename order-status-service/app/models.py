from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, nullable=False)
    requester_id = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    requested = Column(Boolean, default=False)
    accepted  = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    paid      = Column(Boolean, default=False)
    alert     = Column(Boolean, default=False)