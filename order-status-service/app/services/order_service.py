from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Order
from app.schemas import OrderCreate, OrderUpdate, OrderStatus
from app.repositories.order_repository import OrderRepository

class OrderService:
    """Encapsulates business rules for Order states."""

    def __init__(self, db: Session):
        self.repo = OrderRepository(db)

    # ---------- Create ----------
    def create(self, data: OrderCreate) -> Order:
        if self.repo.get_by_order_id(data.order_id):
            raise HTTPException(status_code=400,
                                detail="The order ID already exists")

        new_order = Order(
            order_id=data.order_id,
            requester_id=data.requester_id,
            created_by=data.created_by
        )
        return self.repo.add(new_order)

    # ---------- Read state ----------
    def status(self, order_id: int) -> OrderStatus:
        order = self._get_or_404(order_id)
        return OrderStatus(
            order_id=order.order_id,
            requested=order.requested,
            accepted=order.accepted,
            completed=order.completed,
            paid=order.paid,
            alert=order.alert
        )

    # ---------- Update state ----------
    def update_state(self, order_id: int, upd: OrderUpdate) -> Order:
        order = self._get_or_404(order_id)

        self._validate_transition(order, upd)

        # Mutate state based on the type
        match upd.state_type:
            case "requested": order.requested = upd.new_value
            case "accepted":  order.accepted  = upd.new_value
            case "completed": order.completed = upd.new_value
            case "paid":      order.paid      = upd.new_value
            case "alert":     order.alert     = upd.new_value
            case _: raise HTTPException(status_code=400,
                                        detail="Invalid state_type")

        return self.repo.save(order)

    # ---------- Helpers ----------
    def _get_or_404(self, order_id: int) -> Order:
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def _validate_transition(self, order: Order, upd: OrderUpdate) -> None:
        """Business rules and permissions."""
        # Permissions by user:
        if upd.state_type in {"requested", "paid"} and upd.user_id != order.requester_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if upd.state_type in {"accepted", "completed"} and upd.username != order.created_by:
            raise HTTPException(status_code=403, detail="Not authorized")

        # State order (cannot skip steps):
        rules = {
            "requested": order.accepted,
            "accepted":  order.completed,
            "completed": order.paid,
            "paid":      order.alert
        }
        if rules.get(upd.state_type, False):
            raise HTTPException(status_code=400,
                                detail=f"Cannot modify {upd.state_type} after later stages")