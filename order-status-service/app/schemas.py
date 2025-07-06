from pydantic import BaseModel

class OrderCreate(BaseModel):
    order_id: int
    requester_id: str
    created_by: str

class OrderStatus(BaseModel):
    order_id: int
    requested: bool
    accepted: bool
    completed: bool
    paid: bool
    alert: bool

class OrderUpdate(BaseModel):
    user_id: str | None = None     # who makes the request
    username: str | None = None    # alias for creator
    new_value: bool
    state_type: str                # requested | accepted | completed | paid | alert