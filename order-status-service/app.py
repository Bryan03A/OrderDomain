import jwt
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Boolean, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
# from fastapi.middleware.cors import CORSMiddleware  # ⛔ CORS desactivado
import uvicorn

# Configuración de la base de datos
DB_URL = "postgresql://admin:admin123@35.168.99.213:5432/mydb"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SECRET_KEY = "mysecretkey"

# Modelo de datos para recibir las solicitudes
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
    user_id: str
    new_value: bool
    state_type: str

# Modelo de Orden en PostgreSQL
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, unique=True, nullable=False)
    requester_id = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    requested = Column(Boolean, default=False)
    accepted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    paid = Column(Boolean, default=False)
    alert = Column(Boolean, default=False)

# Crear la tabla en la base de datos si no existe
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI()

# 🔒 CORS eliminado porque se maneja en NGINX
# origins = [
#     "http://3.227.120.143:8080",
#     "http://3.224.44.87:5007",
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/orders/")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    existing_order = db.query(Order).filter(Order.order_id == order_data.order_id).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="El ID de la orden ya existe")
    
    new_order = Order(
        order_id=order_data.order_id,
        requester_id=order_data.requester_id,
        created_by=order_data.created_by
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"message": "Orden creada exitosamente", "order": new_order}

@app.get("/orders/{order_id}/status")
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    return {
        "order_id": order.order_id,
        "requester_id": order.requester_id,
        "created_by": order.created_by,
        "requested": order.requested,
        "accepted": order.accepted,
        "completed": order.completed,
        "paid": order.paid,
        "alert": order.alert
    }

@app.put("/orders/{order_id}/update")
def update_order(order_id: int, update_data: OrderUpdate, request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth_header.split(" ")[1]
    token_payload = verify_token(token)
    token_user_id = token_payload.get("user_id")

    print("🔐 Token payload:", token_payload)
    print("📦 Update data:", update_data.dict())

    if token_user_id != update_data.user_id:
        raise HTTPException(status_code=403, detail="User ID in token does not match user ID in request")

    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Validaciones de estado y permisos como las tenías...

    if order.accepted and update_data.state_type == "requested":
        raise HTTPException(status_code=400, detail="Cannot change 'requested' after 'accepted' is true")
    if order.completed and update_data.state_type == "accepted":
        raise HTTPException(status_code=400, detail="Cannot change 'accepted' after 'completed' is true")
    if order.paid and update_data.state_type == "completed":
        raise HTTPException(status_code=400, detail="Cannot change 'completed' after 'paid' is true")
    if order.alert and update_data.state_type == "paid":
        raise HTTPException(status_code=400, detail="Cannot change 'paid' after 'alert' is true")

    if update_data.state_type == "alert":
        order.alert = update_data.new_value
    elif update_data.state_type == "requested" and update_data.user_id == order.requester_id:
        order.requested = update_data.new_value
    elif update_data.state_type == "accepted" and update_data.user_id == order.created_by:
        if not order.requested:
            raise HTTPException(status_code=400, detail="Cannot accept before requested")
        order.accepted = update_data.new_value
    elif update_data.state_type == "completed" and update_data.user_id == order.created_by:
        if not order.accepted:
            raise HTTPException(status_code=400, detail="Cannot complete before accepted")
        order.completed = update_data.new_value
    elif update_data.state_type == "paid" and update_data.user_id == order.requester_id:
        if not order.completed:
            raise HTTPException(status_code=400, detail="Cannot pay before completed")
        order.paid = update_data.new_value
    else:
        raise HTTPException(status_code=403, detail="Permission denied to update this state")

    db.commit()
    db.refresh(order)
    return {"message": f"State {update_data.state_type} updated", "order": order}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5017, reload=True)
