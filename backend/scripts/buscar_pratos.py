import argparse

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from gerar_embeddings import DATABASE_URL, MODEL_NAME


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca semântica do FoodMatch")
    parser.add_argument("consulta", help="Descreva o que você quer comer")
    args = parser.parse_args()

    consulta = args.consulta.strip()
    if not consulta:
        parser.error("Digite uma descrição para buscar.")

    print("Carregando o modelo...", flush=True)
    modelo = SentenceTransformer(MODEL_NAME, device="cpu")
    vetor = modelo.encode(consulta, normalize_embeddings=True)

    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        register_vector(conn)
        resultados = conn.execute(
            """
            SELECT d.name, r.name, d.price,
                   d.embedding <=> %s AS distancia
            FROM dishes AS d
            JOIN restaurants AS r ON r.id = d.restaurant_id
            WHERE d.embedding IS NOT NULL
            ORDER BY distancia ASC, d.id ASC
            LIMIT 5
            """,
            (vetor,),
        ).fetchall()

    if not resultados:
        print("Nenhum prato com embedding. Execute gerar_embeddings.py primeiro.")
        return

    print(f"\nResultados para «{consulta}»\n")
    for posicao, (prato, restaurante, preco, distancia) in enumerate(resultados, 1):
        similaridade = 1 - distancia
        preco_formatado = f"{preco:.2f}".replace(".", ",")
        print(
            f"{posicao}. {prato} | {restaurante} | "
            f"R$ {preco_formatado} | similaridade {similaridade:.3f}"
        )


if __name__ == "__main__":
    main()