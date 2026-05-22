from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
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


class LeadBase(BaseModel):
    nombre: str
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    estado: Optional[str] = None
    fuente: Optional[str] = None
    notas: Optional[str] = None
    sheets_row_id: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    estado: Optional[str] = None
    fuente: Optional[str] = None
    notas: Optional[str] = None
    sheets_row_id: Optional[str] = None


class LeadOut(LeadBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime]

    class Config:
        from_attributes = True


class InteraccionBase(BaseModel):
    lead_id: Optional[int] = None
    tipo: Optional[str] = None
    contenido: Optional[str] = None
    fecha: Optional[str] = None
    agente: Optional[str] = None
    sheets_row_id: Optional[str] = None


class InteraccionCreate(InteraccionBase):
    pass


class InteraccionUpdate(BaseModel):
    lead_id: Optional[int] = None
    tipo: Optional[str] = None
    contenido: Optional[str] = None
    fecha: Optional[str] = None
    agente: Optional[str] = None
    sheets_row_id: Optional[str] = None


class InteraccionOut(InteraccionBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True
