from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import LoginRequest, Token, UsuarioCreate, UsuarioOut
from auth.utils import hash_password, verify_password, create_access_token, EXPIRE_HRS
import models

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _ensure_usuario_profile_columns(db: Session) -> None:
    existing_columns = {
        row[1] for row in db.execute(text("PRAGMA table_info(usuarios)")).fetchall()
    }
    schema_changed = False

    if "nombre" not in existing_columns:
        db.execute(text("ALTER TABLE usuarios ADD COLUMN nombre VARCHAR"))
        schema_changed = True

    db.execute(text("UPDATE usuarios SET nombre = '' WHERE nombre IS NULL"))

    if schema_changed:
        db.commit()
        return

    db.commit()


@router.post("/register", response_model=UsuarioOut, status_code=201)
def register(payload: UsuarioCreate, db: Session = Depends(get_db)):
    _ensure_usuario_profile_columns(db)

    exists = db.query(models.Usuario).filter(
        models.Usuario.correo == payload.correo
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo = models.Usuario(
        nombre=payload.nombre.strip(),
        correo=payload.correo.lower(),
        password=hash_password(payload.password)
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    _ensure_usuario_profile_columns(db)

    user = db.query(models.Usuario).filter(
        models.Usuario.correo == payload.correo.lower()
    ).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token = create_access_token({"sub": user.correo})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": EXPIRE_HRS * 3600
    }
