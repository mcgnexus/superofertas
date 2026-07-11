"""Modelos de base de datos con SQLAlchemy."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import os

Base = declarative_base()


class Supermercado(Base):
    __tablename__ = "supermercados"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    ubicacion = Column(String, default="")
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    productos = relationship("Producto", back_populates="supermercado")
    ofertas = relationship("Oferta", back_populates="supermercado")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    categoria = Column(String, index=True)
    precio_unitario = Column(Float)
    supermercado_id = Column(Integer, ForeignKey("supermercados.id"))
    imagen_url = Column(String, default="")
    url_producto = Column(String, default="")
    unidad = Column(String, default="ud")

    supermercado = relationship("Supermercado", back_populates="productos")
    ofertas = relationship("Oferta", back_populates="producto")


class Oferta(Base):
    __tablename__ = "ofertas"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    supermercado_id = Column(Integer, ForeignKey("supermercados.id"))
    precio_oferta = Column(Float)
    precio_normal = Column(Float, nullable=True)
    descuento = Column(Integer, default=0)
    fecha_inicio = Column(DateTime, default=datetime.now)
    fecha_fin = Column(DateTime, nullable=True)

    producto = relationship("Producto", back_populates="ofertas")
    supermercado = relationship("Supermercado", back_populates="ofertas")
    menus = relationship("Menu", back_populates="oferta")


class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"))
    dia = Column(Integer)          # 1-7
    comida = Column(Integer)       # 1-5
    nombre_plato = Column(String)
    instrucciones = Column(Text)
    ingredientes = Column(Text)    # JSON serializado
    tiempo_minutos = Column(Integer, nullable=True)
    calorias_aprox = Column(Integer, nullable=True)

    menu = relationship("Menu", back_populates="recetas")


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    oferta_id = Column(Integer, ForeignKey("ofertas.id"), nullable=True)
    presupuesto = Column(Float)
    num_personas = Column(Integer)
    restricciones = Column(Text, nullable=True)  # JSON serializado
    fecha_creacion = Column(DateTime, default=datetime.now)

    oferta = relationship("Oferta", back_populates="menus")
    recetas = relationship("Receta", back_populates="menu")


# Engine y sesión - se inicializa con variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ofertas.db"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
