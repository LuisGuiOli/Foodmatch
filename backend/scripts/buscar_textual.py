import argparse

import psycopg

from gerar_embeddings import DATABASE_URL


BUSCA_TEXTUAL = """
WITH consulta AS (
    SELECT plainto_tsquery('portuguese', %s) AS termos
),
catalogo AS (
    SELECT
        d.id,
        d.name AS prato,
        r.name AS restaurante,
        to_tsvector(
            'portuguese',
            concat_ws(' ', d.name, d.category, d.description)
        ) AS documento
    FROM dishes AS d
    JOIN restaurants AS r ON r.id = d.restaurant_id
)
SELECT c.id, c.prato, c.restaurante,
       ts_rank(c.documento, q.termos) AS score
FROM catalogo AS c
CROSS JOIN consulta AS q
WHERE c.documento @@ q.termos
ORDER BY score DESC, c.id ASC
LIMIT 5
"""


def buscar_textual(conn, consulta: str):
    return conn.execute(BUSCA_TEXTUAL, (consulta,)).fetchall()


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca textual do FoodMatch")
    parser.add_argument("consulta", help="Palavras para buscar no catálogo")
    args = parser.parse_args()

    consulta = args.consulta.strip()
    if not consulta:
        parser.error("Digite uma consulta.")

    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        resultados = buscar_textual(conn, consulta)

    if not resultados:
        print("Nenhum prato encontrado para esses termos.")
        return

    for posicao, (prato_id, prato, restaurante, score) in enumerate(resultados, 1):
        print(f"{posicao}. {prato} | {restaurante} | id={prato_id} | score={score:.3f}")


if __name__ == "__main__":
    main()