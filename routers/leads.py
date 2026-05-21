from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth.dependencies import get_current_user
from schemas import LeadOut
import models

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("/", response_model=List[LeadOut])
def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    estado: Optional[str] = None,
    buscar: Optional[str] = None,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    query = db.query(models.Lead)
    if estado:
        query = query.filter(models.Lead.estado == estado)
    if buscar:
        query = query.filter(
            models.Lead.nombre.ilike(f"%{buscar}%") |
            models.Lead.correo.ilike(f"%{buscar}%")
        )
    return query.offset(skip).limit(limit).all()


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead
