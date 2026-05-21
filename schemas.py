from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UsuarioCreate(BaseModel):
    correo: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    correo: EmailStr
    creado_en: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class LeadOut(BaseModel):
    id: int
    nombre: str
    correo: Optional[str]
    telefono: Optional[str]
    empresa: Optional[str]
    estado: Optional[str]
    fuente: Optional[str]
    notas: Optional[str]
    sheets_row_id: Optional[str]
    creado_en: datetime

    class Config:
        from_attributes = True


class InteraccionOut(BaseModel):
    id: int
    lead_id: Optional[int]
    tipo: Optional[str]
    contenido: Optional[str]
    fecha: Optional[str]
    agente: Optional[str]
    sheets_row_id: Optional[str]
    creado_en: datetime

    class Config:
        from_attributes = True
