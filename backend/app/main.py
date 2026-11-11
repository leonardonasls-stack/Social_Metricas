from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import niches, analyses


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Criação automática de tabelas na inicialização (em dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Métrica Social-Media API",
    version="1.0.0",
    description="Backend de Inteligência Social para Construtores de Aplicações e Landing Pages",
    lifespan=lifespan
)

# Configuração de CORS para permitir comunicação do frontend Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão de Routers da v1
app.include_router(niches.router, prefix="/api/v1")
app.include_router(analyses.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "metrica-social-media-backend",
        "mode": settings.DEFAULT_MINING_MODE
    }
