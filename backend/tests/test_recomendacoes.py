import httpx
import pytest


URL = "http://127.0.0.1:8000/api/recomendacoes"


@pytest.mark.parametrize("orcamento", [None, 20])
def test_retorna_cinco_pratos_em_ordem_de_score(orcamento):
    pedido = {"consulta": "quero frango para o almoço"}
    if orcamento is not None:
        pedido["orcamento"] = orcamento

    resposta = httpx.post(URL, json=pedido, timeout=30)

    assert resposta.status_code == 200, resposta.text
    pratos = resposta.json()

    # O catálogo inicial tem seis pratos vetorizados e a API retorna os cinco primeiros.
    assert len(pratos) == 5
    assert len({prato["id"] for prato in pratos}) == 5

    for prato in pratos:
        assert prato["prato"].strip()
        assert prato["restaurante"].strip()
        assert prato["preco"] > 0

    scores = [prato["score"] for prato in pratos]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize(
    "pedido",
    [
        {"consulta": "   "},
        {"consulta": "frango", "orcamento": 0},
        {"consulta": "frango", "orcamento": -10},
    ],
)
def test_rejeita_pedido_invalido(pedido):
    resposta = httpx.post(URL, json=pedido, timeout=10)
    assert resposta.status_code == 422, resposta.text