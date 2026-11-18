# FoodMatch

O FoodMatch recomenda pratos a partir de um pedido em português e de um orçamento opcional. Para uma busca como “quero frango para o almoço, até R$ 20”, o React extrai o valor e envia o texto e o orçamento à API. O PostgreSQL combina a proximidade semântica com as avaliações e o preço para devolver até cinco pratos.

## Como funciona

1. O script de carga importa restaurantes, pratos e avaliações do CSV. Executá-lo novamente atualiza os registros pelos IDs.
2. O MiniLM multilíngue transforma nome, categoria e descrição de cada prato em um vetor de 384 dimensões. O pgvector guarda esses vetores na tabela `dishes`. Alterações nesses campos tornam o vetor pendente para recálculo.
3. Na inicialização, o FastAPI carrega o modelo em CPU. A cada busca, calcula apenas o vetor da consulta.
4. A API ordena os pratos pelo score híbrido. O frontend mantém a ordem recebida e permite filtrar os resultados por restaurante.

A vitrine inicial tem fotos e cardápios ilustrativos da referência visual. Ao buscar, a grade exibe os nomes, restaurantes, preços e scores devolvidos pela API. O filtro de orçamento orienta o ranking e pode retornar pratos acima do valor informado. Os favoritos ficam na memória da página até que ela seja recarregada.

## Ranking

Com orçamento, o score é `0,65 × S + 0,20 × A + 0,15 × P`.

| Sinal | Cálculo |
| --- | --- |
| S · Similaridade | 1 menos a distância de cosseno entre os embeddings da consulta e do prato |
| A · Avaliação | (nota − 1) / 4, usando a média do prato e, quando ausente, a nota do restaurante |
| P · Preço | Mínimo entre 1 e orçamento / preço |

Sem orçamento, o score é `(0,65 × S + 0,20 × A) / 0,85`. A similaridade e o score são valores de ordenação. O projeto não estima uma probabilidade de aceitação.

## Execução local

Requisitos: Docker com Compose, Python 3.12 com venv e Node.js 22.12+ com npm. No WSL, execute os comandos com os binários de Linux. Os exemplos partem da raiz do repositório.

**1. Subir o banco e a API**

```bash
docker compose up -d --build db api
docker compose logs -f api
```

Na primeira execução, aguarde o download do modelo e a mensagem `Application startup complete`. Use Ctrl+C para sair dos logs. A API e o banco continuam em execução. O Compose publica a API na porta 8000 e o PostgreSQL na 5433.

**2. Preparar o catálogo em uma instalação nova**

```bash
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python backend/scripts/seed.py
backend/.venv/bin/python backend/scripts/gerar_embeddings.py
```

Os scripts usam a porta 5433 no WSL. Dentro do Compose, a API acessa o serviço `db:5432`. O Python local e o container usam caches distintos para o modelo. Uma instalação já populada pode seguir diretamente para o frontend.

**3. Abrir a interface**

```bash
cd frontend
npm ci
npm run dev
```

Abra [FoodMatch](http://localhost:5173). O Vite encaminha `/api` para `http://127.0.0.1:8000`. Para compilar a interface, execute `npm run build` em `frontend/`.

## API

A documentação interativa fica em [Swagger UI](http://127.0.0.1:8000/docs). Exemplo de busca:

```bash
curl -sS http://127.0.0.1:8000/api/recomendacoes -H 'Content-Type: application/json' -d '{"consulta":"quero frango para o almoço","orcamento":20}'
```

A resposta é uma lista ordenada com `id`, `prato`, `restaurante`, `preco` e `score`. Omitir `orcamento` ativa o ranking sem preço. Consultas em branco e orçamentos menores ou iguais a zero retornam HTTP 422.

## Avaliação do ranking

O experimento usa 20 consultas rotuladas e um catálogo fictício de seis pratos de três restaurantes. Os rótulos atribuem relevância de 0, 1 ou 2 a cada par consulta–prato. A busca textual usa o dicionário português do PostgreSQL, a semântica usa distância de cosseno e a híbrida combina os três sinais.

| Método | Precision@5 | NDCG@5 |
| --- | ---: | ---: |
| Textual | 0,060 | 0,300 |
| Semântica | 0,250 | 0,917 |
| Híbrida | 0,250 | **0,951** |

Há 25 pares relevantes nas 100 posições avaliadas. As buscas semântica e híbrida atingiram a Precision@5 máxima possível para esses rótulos. A híbrida ganhou 0,034 ponto de NDCG@5 em relação à semântica. Esse resultado indica melhora média na ordem dos pratos para este conjunto pequeno. O experimento mede o efeito conjunto dos sinais de nota e preço.

Para reproduzir as métricas e os cinco testes de integração, mantenha o banco populado e a API em execução. Na raiz do projeto:

```bash
backend/.venv/bin/python backend/scripts/avaliar_buscas.py
backend/.venv/bin/python -m pytest -q backend/tests/test_recomendacoes.py
```

## Organização

| Caminho | Conteúdo |
| --- | --- |
| `backend/app/main.py` | Ciclo de vida do modelo, validação e rota de recomendação |
| `backend/scripts/` | Carga, embeddings, buscas, SQL compartilhado e avaliação |
| `backend/tests/` | Testes do contrato HTTP |
| `data/` | Catálogo CSV e consultas rotuladas |
| `frontend/src/` | Tela React, dados da vitrine e estilos responsivos |
| `frontend/public/foodmatch/` | Imagens ilustrativas da vitrine |
| `docker-compose.yml` | PostgreSQL com pgvector e API em CPU |
