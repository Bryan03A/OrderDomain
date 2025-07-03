from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Boolean, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configuración de la base de datos
DB_URL = "postgresql://postgres.imfqyzgimtercyyqeqof:1997Guallaba@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    user_id: str  # Cambiar de int a str para que acepte UUID
    new_value: bool
    state_type: str  # requested, accepted, completed, paid, alert # requested, accepted, completed, paid, alert

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

origins = [
    "http://3.212.132.24:8080",  # Permite solicitudes desde la interfaz (puerto 8080)
    "http://34.228.5.25:5007",
]

# Agregar el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite solo el origen de la interfaz
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def update_order(order_id: int, update_data: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    # Verificación de las condiciones para bloquear la actualización de los estados
    if order.accepted and update_data.state_type == "requested":
        raise HTTPException(status_code=400, detail="No se puede modificar el estado 'requested' después de que 'accepted' sea true")
    
    if order.completed and update_data.state_type == "accepted":
        raise HTTPException(status_code=400, detail="No se puede modificar el estado 'accepted' después de que 'completed' sea true")
    
    if order.paid and update_data.state_type == "completed":
        raise HTTPException(status_code=400, detail="No se puede modificar el estado 'completed' después de que 'paid' sea true")
    
    if order.alert and update_data.state_type == "paid":
        raise HTTPException(status_code=400, detail="No se puede modificar el estado 'paid' después de que 'alert' sea true")

    # Lógica para actualizar el estado según el tipo
    if update_data.state_type == "alert":
        order.alert = update_data.new_value
    elif update_data.state_type == "requested" and update_data.user_id == order.requester_id:
        order.requested = update_data.new_value
    elif update_data.state_type == "accepted" and update_data.user_id == order.created_by:
        if not order.requested:
            raise HTTPException(status_code=400, detail="No puedes aceptar antes de que sea solicitado")
        order.accepted = update_data.new_value
    elif update_data.state_type == "completed" and update_data.user_id == order.created_by:
        if not order.accepted:
            raise HTTPException(status_code=400, detail="No puedes completar antes de que sea aceptado")
        order.completed = update_data.new_value
    elif update_data.state_type == "paid" and update_data.user_id == order.requester_id:
        if not order.completed:
            raise HTTPException(status_code=400, detail="No puedes pagar antes de que sea completado")
        order.paid = update_data.new_value
    else:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar este estado")

    db.commit()
    db.refresh(order)
    return {"message": f"Estado {update_data.state_type} actualizado", "order": order}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5017, reload=True)