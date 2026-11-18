import argparse
from decimal import Decimal, InvalidOperation

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from gerar_embeddings import DATABASE_URL, MODEL_NAME

from ranking_sql import BUSCA_HIBRIDA

def ler_orcamento(valor: str) -> Decimal:
    try:
        orcamento = Decimal(valor.replace(",", "."))
    except InvalidOperation:
        raise argparse.ArgumentTypeError("Use um valor como 25 ou 19,90.") from None

    if not orcamento.is_finite() or orcamento <= 0:
        raise argparse.ArgumentTypeError("O orçamento deve ser maior que zero.")

    return orcamento





def main() -> None:
    parser = argparse.ArgumentParser(description="Ranking híbrido do FoodMatch")
    parser.add_argument("consulta", help="Descreva o que deseja comer")
    parser.add_argument("--orcamento", type=ler_orcamento, help="Valor em reais")
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
            BUSCA_HIBRIDA,
            {"vetor": vetor, "orcamento": args.orcamento},
        ).fetchall()

    if not resultados:
        print("Nenhum prato com embedding disponível.")
        return

    # for posicao, (prato, restaurante, preco, s, a, p, score) in enumerate(resultados, 1):
    for posicao, (prato_id, prato, restaurante, preco, s, a, p, score) in enumerate(resultados, 1):
        preco_reais = f"{preco:.2f}".replace(".", ",")
        componente_preco = "—" if p is None else f"{p:.3f}"
        print(f"{posicao}. {prato} | {restaurante} | R$ {preco_reais}")
        print(f"   S={s:.3f}  A={a:.3f}  P={componente_preco}  score={score:.3f}")


if __name__ == "__main__":
    main()


# SELECT prato, restaurante, preco, s, a, p,
