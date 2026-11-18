import os

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://foodmatch:foodmatch_dev@127.0.0.1:5433/foodmatch",
)


def main() -> None:
    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        pratos = conn.execute(
            """
            SELECT id, name, category, description
            FROM dishes
            WHERE embedding IS NULL
            ORDER BY id
            """
        ).fetchall()

    if not pratos:
        print("Nenhum prato pendente.")
        return

    print(f"{len(pratos)} prato(s) pendente(s). Carregando o modelo...", flush=True)
    modelo = SentenceTransformer(MODEL_NAME, device="cpu")
    textos = [
        f"{nome}. Categoria: {categoria}. {descricao}"
        for _, nome, categoria, descricao in pratos
    ]
    vetores = modelo.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    gravados = 0
    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        register_vector(conn)
        for (prato_id, nome, categoria, descricao), vetor in zip(
            pratos, vetores, strict=True
        ):
            resultado = conn.execute(
                """
                UPDATE dishes
                SET embedding = %s
                WHERE id = %s AND embedding IS NULL
                  AND name = %s AND category = %s AND description = %s
                """,
                (vetor, prato_id, nome, categoria, descricao),
            )
            gravados += resultado.rowcount

    print(f"Embeddings gravados: {gravados}.")


if __name__ == "__main__":
    main()