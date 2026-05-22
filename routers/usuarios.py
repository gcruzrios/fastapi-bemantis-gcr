from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth.dependencies import get_current_user
from schemas import UsuarioOut
import models

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioOut])
def get_usuarios(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    usuarios = db.query(models.Usuario).all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioOut)
def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
