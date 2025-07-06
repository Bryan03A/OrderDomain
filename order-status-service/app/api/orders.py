from fastapi import APIRouter, Depends, status
from app.schemas import OrderCreate, OrderStatus, OrderUpdate
from app.services.order_service import OrderService
from app.dependencies import get_order_service

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    svc: OrderService = Depends(get_order_service)
):
    return {"message": "Order created successfully",
            "order": svc.create(payload)}

@router.get("/{order_id}/status", response_model=OrderStatus)
def get_status(
    order_id: int,
    svc: OrderService = Depends(get_order_service)
):
    return svc.status(order_id)

@router.put("/{order_id}/update")
def update_order(
    order_id: int,
    payload: OrderUpdate,
    svc: OrderService = Depends(get_order_service)
):
    order = svc.update_state(order_id, payload)
    return {"message": f"State {payload.state_type} updated",
            "order": order}