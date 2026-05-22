from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth.dependencies import get_current_user
from schemas import LeadCreate, LeadOut, LeadUpdate
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
            or_(
                models.Lead.nombre.ilike(f"%{buscar}%"),
                models.Lead.correo.ilike(f"%{buscar}%"),
                models.Lead.telefono.ilike(f"%{buscar}%"),
                models.Lead.empresa.ilike(f"%{buscar}%"),
                models.Lead.estado.ilike(f"%{buscar}%"),
                models.Lead.fuente.ilike(f"%{buscar}%"),
                models.Lead.notas.ilike(f"%{buscar}%"),
                models.Lead.sheets_row_id.ilike(f"%{buscar}%"),
            )
        )

    return (
        query
        .order_by(models.Lead.creado_en.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


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


@router.post("/", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    lead = models.Lead(**payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    has_interactions = (
        db.query(models.Interaccion.id)
        .filter(models.Interaccion.lead_id == lead_id)
        .first()
    )
    if has_interactions:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el lead porque tiene interacciones asociadas"
        )

    db.delete(lead)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
