"""
Servicio que hace polling a Google Sheets cada N minutos.
Lee las pestañas Leads e Interacciones y sincroniza con SQLite.
"""
import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID   = os.getenv("SPREADSHEET_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_sheets_client() -> gspread.Client:
    creds  = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


def sync_leads(db: Session):
    client      = get_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet   = spreadsheet.worksheet("Leads")
    rows        = worksheet.get_all_records()

    for row in rows:
        row_id = str(row.get("row_id") or row.get("ID") or "")
        if not row_id:
            continue

        existing = db.query(models.Lead).filter(
            models.Lead.sheets_row_id == row_id
        ).first()

        if existing:
            existing.nombre   = row.get("nombre", existing.nombre)
            existing.correo   = row.get("correo", existing.correo)
            existing.telefono = row.get("telefono", existing.telefono)
            existing.empresa  = row.get("empresa", existing.empresa)
            existing.estado   = row.get("estado", existing.estado)
            existing.fuente   = row.get("fuente", existing.fuente)
            existing.notas    = row.get("notas", existing.notas)
        else:
            nuevo = models.Lead(
                sheets_row_id = row_id,
                nombre        = row.get("nombre", "Sin nombre"),
                correo        = row.get("correo"),
                telefono      = row.get("telefono"),
                empresa       = row.get("empresa"),
                estado        = row.get("estado", "Nuevo"),
                fuente        = row.get("fuente"),
                notas         = row.get("notas"),
            )
            db.add(nuevo)

    db.commit()
    print(f"[Sync] Leads sincronizados: {len(rows)} filas")


def sync_interacciones(db: Session):
    client      = get_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet   = spreadsheet.worksheet("Interacciones")
    rows        = worksheet.get_all_records()

    for row in rows:
        row_id = str(row.get("row_id") or row.get("ID") or "")
        if not row_id:
            continue

        lead_sheets_id = str(row.get("lead_row_id") or "")
        lead = None
        if lead_sheets_id:
            lead = db.query(models.Lead).filter(
                models.Lead.sheets_row_id == lead_sheets_id
            ).first()

        existing = db.query(models.Interaccion).filter(
            models.Interaccion.sheets_row_id == row_id
        ).first()

        if existing:
            existing.tipo      = row.get("tipo", existing.tipo)
            existing.contenido = row.get("contenido", existing.contenido)
            existing.fecha     = row.get("fecha", existing.fecha)
            existing.agente    = row.get("agente", existing.agente)
            if lead:
                existing.lead_id = lead.id
        else:
            nueva = models.Interaccion(
                sheets_row_id = row_id,
                lead_id       = lead.id if lead else None,
                tipo          = row.get("tipo"),
                contenido     = row.get("contenido"),
                fecha         = row.get("fecha"),
                agente        = row.get("agente"),
            )
            db.add(nueva)

    db.commit()
    print(f"[Sync] Interacciones sincronizadas: {len(rows)} filas")


def run_sync():
    """Función principal llamada por el scheduler."""
    db = SessionLocal()
    try:
        sync_leads(db)
        sync_interacciones(db)
    except Exception as e:
        print(f"[Sync ERROR] {e}")
    finally:
        db.close()
