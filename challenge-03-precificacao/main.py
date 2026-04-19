"""
HAT Thinking — Challenge 03: Motor de Precificação de Propostas
Ponto de entrada da aplicação FastAPI.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import propostas
from src.infra.database import create_db_and_tables
from src.domain.services.precificacao import TABELA_PRECOS


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="HAT Challenge 03 — Motor de Precificação",
    description="API para criação, validação e aprovação de propostas comerciais de Professional Services.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(propostas.router, prefix="/propostas", tags=["Propostas"])


@app.get("/tabela-precos", tags=["Configuração"])
def tabela_precos():
    return [
        {
            "senioridade": senioridade.value,
            "custo_hora": str(precos["custo"]),
            "venda_hora": str(precos["venda"]),
        }
        for senioridade, precos in TABELA_PRECOS.items()
    ]


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "challenge": "03-precificacao"}