"""FastAPI entry point for Landlorded backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import audits, documents, users
from .services.audit_service import get_corpus

app = FastAPI(title="Landlorded API", version="1.0.0")

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(audits.router)
app.include_router(documents.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup():
    get_corpus()  # Pre-load corpus into memory


@app.get("/health")
async def health():
    return {"status": "ok"}
