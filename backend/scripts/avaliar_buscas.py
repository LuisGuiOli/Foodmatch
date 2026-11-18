import json
from math import log2
from pathlib import Path
from statistics import mean

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from buscar_hibrido import BUSCA_HIBRIDA
from buscar_textual import buscar_textual
from gerar_embeddings import DATABASE_URL, MODEL_NAME


ARQUIVO_CONSULTAS = (
    Path(__file__).resolve().parents[2] / "data" / "consultas_avaliacao.json"
)
K = 5

BUSCA_SEMANTICA = """
SELECT id
FROM dishes
WHERE embedding IS NOT NULL
ORDER BY embedding <=> %s, id
LIMIT 5
"""


def calcular_metricas(ids, relevancia):
    notas = [relevancia.get(prato_id, 0) for prato_id in ids[:K]]
    precision = sum(nota > 0 for nota in notas) / K

    def dcg(notas_ordenadas):
        return sum(
            (2**nota - 1) / log2(posicao + 2)
            for posicao, nota in enumerate(notas_ordenadas)
        )

    notas_ideais = sorted(relevancia.values(), reverse=True)[:K]
    ideal = dcg(notas_ideais)
    ndcg = dcg(notas) / ideal if ideal else 0.0
    return precision, ndcg


def main():
    casos = json.loads(ARQUIVO_CONSULTAS.read_text(encoding="utf-8"))
    resultados = {"textual": [], "semantica": [], "hibrida": []}

    with psycopg.connect(DATABASE_URL, connect_timeout=5, autocommit=True) as conn:
        register_vector(conn)

        catalogo = conn.execute("SELECT id, embedding IS NOT NULL FROM dishes").fetchall()
        ids_catalogo = {prato_id for prato_id, _ in catalogo}
        ids_rotulados = {
            int(prato_id) for caso in casos for prato_id in caso["relevancia"]
        }
        if ids_rotulados - ids_catalogo:
            raise SystemExit(f"IDs dos rótulos ausentes no banco: {ids_rotulados - ids_catalogo}")
        if any(not tem_vetor for _, tem_vetor in catalogo):
            raise SystemExit("Há pratos sem vetor. Execute gerar_embeddings.py primeiro.")

        print(f"Carregando o modelo para avaliar {len(casos)} consultas...", flush=True)
        modelo = SentenceTransformer(MODEL_NAME, device="cpu")
        vetores = modelo.encode(
            [caso["consulta"] for caso in casos],
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        for caso, vetor in zip(casos, vetores, strict=True):
            consulta = caso["consulta"]
            relevancia = {int(id_): nota for id_, nota in caso["relevancia"].items()}

            rankings = {
                "textual": buscar_textual(conn, consulta),
                "semantica": conn.execute(BUSCA_SEMANTICA, (vetor,)).fetchall(),
                "hibrida": conn.execute(
                    BUSCA_HIBRIDA,
                    {"vetor": vetor, "orcamento": caso.get("orcamento")},
                ).fetchall(),
            }

            for metodo, linhas in rankings.items():
                ids = [linha[0] for linha in linhas]
                resultados[metodo].append(calcular_metricas(ids, relevancia))

    print(f"\n{'Método':<12} {'Precision@5':>12} {'NDCG@5':>10}")
    for metodo, metricas in resultados.items():
        precisions, ndcgs = zip(*metricas)
        print(f"{metodo:<12} {mean(precisions):>12.3f} {mean(ndcgs):>10.3f}")


if __name__ == "__main__":
    main()