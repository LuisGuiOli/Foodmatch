import os
from contextlib import asynccontextmanager
from typing import Annotated

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pgvector.psycopg import register_vector
from pydantic import BaseModel, Field, StringConstraints
from sentence_transformers import SentenceTransformer

from scripts.ranking_sql import BUSCA_HIBRIDA


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://foodmatch:foodmatch_dev@127.0.0.1:5433/foodmatch",
)


class BuscaRequest(BaseModel):
    consulta: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
    ]
    orcamento: Annotated[float, Field(gt=0, allow_inf_nan=False)] | None = None


class PratoRecomendado(BaseModel):
    id: int
    prato: str
    restaurante: str
    preco: float
    score: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.modelo = SentenceTransformer(MODEL_NAME, device="cpu")
    yield


app = FastAPI(title="FoodMatch API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.post("/api/recomendacoes", response_model=list[PratoRecomendado])
def recomendar(busca: BuscaRequest, request: Request):
    vetor = request.app.state.modelo.encode(
        busca.consulta,
        normalize_embeddings=True,
    )

    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
            register_vector(conn)
            linhas = conn.execute(
                BUSCA_HIBRIDA,
                {"vetor": vetor, "orcamento": busca.orcamento},
            ).fetchall()
    except psycopg.OperationalError as erro:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível. Verifique o serviço db.",
        ) from erro

    return [
        PratoRecomendado(
            id=prato_id,
            prato=prato,
            restaurante=restaurante,
            preco=preco,
            score=score,
        )
        for prato_id, prato, restaurante, preco, _, _, _, score in linhas
    ]