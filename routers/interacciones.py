from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth.dependencies import get_current_user
from schemas import InteraccionCreate, InteraccionOut, InteraccionUpdate
import models

router = APIRouter(prefix="/interacciones", tags=["Interacciones"])


@router.get("/", response_model=List[InteraccionOut])
def get_interacciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    lead_id: Optional[int] = None,
    buscar: Optional[str] = None,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    query = db.query(models.Interaccion)

    if lead_id is not None:
        query = query.filter(models.Interaccion.lead_id == lead_id)

    if buscar:
        query = query.filter(
            or_(
                models.Interaccion.tipo.ilike(f"%{buscar}%"),
                models.Interaccion.contenido.ilike(f"%{buscar}%"),
                models.Interaccion.fecha.ilike(f"%{buscar}%"),
                models.Interaccion.agente.ilike(f"%{buscar}%"),
                models.Interaccion.sheets_row_id.ilike(f"%{buscar}%"),
            )
        )

    return (
        query
        .order_by(models.Interaccion.creado_en.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{interaccion_id}", response_model=InteraccionOut)
def get_interaccion(
    interaccion_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    obj = (
        db.query(models.Interaccion)
        .filter(models.Interaccion.id == interaccion_id)
        .first()
    )

    if not obj:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")

    return obj


def _ensure_lead_exists(db: Session, lead_id: Optional[int]) -> None:
    if lead_id is None:
        return

    lead = db.query(models.Lead.id).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")


@router.post("/", response_model=InteraccionOut, status_code=status.HTTP_201_CREATED)
def create_interaccion(
    payload: InteraccionCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    _ensure_lead_exists(db, payload.lead_id)

    interaccion = models.Interaccion(**payload.model_dump())
    db.add(interaccion)
    db.commit()
    db.refresh(interaccion)
    return interaccion


@router.put("/{interaccion_id}", response_model=InteraccionOut)
def update_interaccion(
    interaccion_id: int,
    payload: InteraccionUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    interaccion = (
        db.query(models.Interaccion)
        .filter(models.Interaccion.id == interaccion_id)
        .first()
    )

    if not interaccion:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")

    changes = payload.model_dump(exclude_unset=True)
    if "lead_id" in changes:
        _ensure_lead_exists(db, changes["lead_id"])

    for field, value in changes.items():
        setattr(interaccion, field, value)

    db.commit()
    db.refresh(interaccion)
    return interaccion


@router.delete("/{interaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaccion(
    interaccion_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    interaccion = (
        db.query(models.Interaccion)
        .filter(models.Interaccion.id == interaccion_id)
        .first()
    )

    if not interaccion:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")

    db.delete(interaccion)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
