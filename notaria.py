from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from datetime import datetime

# Conexión a la base de datos MySQL
DATABASE_URL = "mysql+pymysqlconnector://root:@localhost:3306/notaria"  # Cambia la contraseña y el nombre de la base de datos

# Configuración de SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la tabla en la base de datos
class Cliente(Base):
    __tablename__ = 'clientes'

    cliente_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    fecha_registro = Column(Date, default=datetime.utcnow)

# Crear la base de datos (si no existe)
Base.metadata.create_all(bind=engine)

# Crear una instancia de FastAPI
app = FastAPI()

# Modelo de datos para un cliente
class ClienteCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None
    fecha_registro: Optional[str] = datetime.utcnow().strftime('%Y-%m-%d')

class ClienteResponse(BaseModel):
    cliente_id: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None
    fecha_registro: str

    class Config:
        orm_mode = True

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para obtener todos los clientes
@app.get("/clientes", response_model=List[ClienteResponse])
def get_clientes(db: Session = next(get_db())):
    clientes = db.query(Cliente).all()
    return clientes

# Endpoint para obtener un cliente por su ID
@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: int, db: Session = next(get_db())):
    cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# Endpoint para crear un nuevo cliente
@app.post("/clientes", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = next(get_db())):
    db_cliente = Cliente(nombre=cliente.nombre, apellido=cliente.apellido, email=cliente.email,
                         telefono=cliente.telefono, fecha_registro=cliente.fecha_registro)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

# Endpoint para eliminar un cliente
@app.delete("/clientes/{cliente_id}", response_model=dict)
def delete_cliente(cliente_id: int, db: Session = next(get_db())):
    cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente eliminado"}

# Página principal de la API con un mensaje amigable
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la Notaría. Use los endpoints disponibles para interactuar."}
