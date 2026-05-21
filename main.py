from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from apscheduler.schedulers.background import BackgroundScheduler
from database import engine
import models
from auth.router import router as auth_router
from routers.leads import router as leads_router
from routers.interacciones import router as interacciones_router
from routers.usuarios import router as usuarios_router
from services.sheets_sync import run_sync
from dotenv import load_dotenv
import os

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CRM API",
    description="Backend para gestión de leads e interacciones con Google Sheets",
    version="1.0.0"
)

SAFE_ORIGINS = [
    "http://localhost:5173",
    "https://dashboard.greiv.in",
    "https://dashboard.bemantis.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=SAFE_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def allow_private_network_requests(request: Request, call_next):
    origin = request.headers.get("origin")
    wants_private_network = (
        request.headers.get("access-control-request-private-network") == "true"
    )

    if request.method == "OPTIONS" and origin in SAFE_ORIGINS and wants_private_network:
        response = Response(status_code=200)
    else:
        response = await call_next(request)

    if origin in SAFE_ORIGINS and wants_private_network:
        response.headers["Access-Control-Allow-Private-Network"] = "true"

    return response

app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(interacciones_router)
app.include_router(usuarios_router)


@app.post("/sync", tags=["Sync"])
def manual_sync():
    run_sync()
    return {"message": "Sincronización completada"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


INTERVAL = int(os.getenv("SYNC_INTERVAL_MINUTES", 5))
scheduler = BackgroundScheduler()
scheduler.add_job(run_sync, "interval", minutes=INTERVAL, id="sheets_sync")


@app.on_event("startup")
def startup_event():
    scheduler.start()
    print(f"[Scheduler] Sync automático cada {INTERVAL} minutos iniciado")


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
