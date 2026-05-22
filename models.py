from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=False)
    empresa     = Column(String, nullable=False)
    correo      = Column(String, unique=True, index=True, nullable=False)
    password    = Column(String, nullable=False)
    creado_en   = Column(DateTime(timezone=True), server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"

    id              = Column(Integer, primary_key=True, index=True)
    nombre          = Column(String, nullable=False)
    correo          = Column(String, index=True)
    telefono        = Column(String)
    empresa         = Column(String)
    estado          = Column(String, default="Nuevo")
    fuente          = Column(String)
    notas           = Column(Text)
    sheets_row_id   = Column(String, unique=True)
    creado_en       = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en  = Column(DateTime(timezone=True), onupdate=func.now())

    interacciones = relationship("Interaccion", back_populates="lead")


class Interaccion(Base):
    __tablename__ = "interacciones"

    id              = Column(Integer, primary_key=True, index=True)
    lead_id         = Column(Integer, ForeignKey("leads.id"), nullable=True)
    tipo            = Column(String)
    contenido       = Column(Text)
    fecha           = Column(String)
    agente          = Column(String)
    sheets_row_id   = Column(String, unique=True)
    creado_en       = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="interacciones")
