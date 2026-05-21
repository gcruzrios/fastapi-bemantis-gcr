from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth.dependencies import get_current_user
from schemas import InteraccionOut
import models

router = APIRouter(prefix="/interacciones", tags=["Interacciones"])


@router.get("/", response_model=List[InteraccionOut])
def get_interacciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    lead_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    query = db.query(models.Interaccion)
    if lead_id:
        query = query.filter(models.Interaccion.lead_id == lead_id)
    return query.order_by(models.Interaccion.creado_en.desc()).offset(skip).limit(limit).all()


@router.get("/{interaccion_id}", response_model=InteraccionOut)
def get_interaccion(
    interaccion_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    obj = db.query(models.Interaccion).filter(
        models.Interaccion.id == interaccion_id
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return obj
