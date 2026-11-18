BUSCA_HIBRIDA = """
WITH notas AS (
    SELECT dish_id, AVG(rating) AS media
    FROM reviews
    GROUP BY dish_id
),
componentes AS (
    SELECT
        d.id,
        d.name AS prato,
        r.name AS restaurante,
        d.price AS preco,
        1 - (d.embedding <=> %(vetor)s) AS s,
        (COALESCE(n.media, r.rating) - 1) / 4 AS a,
        CASE WHEN %(orcamento)s::numeric IS NOT NULL
             THEN LEAST(1.0, %(orcamento)s::numeric / d.price)
        END AS p
    FROM dishes AS d
    JOIN restaurants AS r ON r.id = d.restaurant_id
    LEFT JOIN notas AS n ON n.dish_id = d.id
    WHERE d.embedding IS NOT NULL
)
SELECT id, prato, restaurante, preco, s, a, p,
       CASE WHEN p IS NULL THEN (0.65 * s + 0.20 * a) / 0.85
            ELSE 0.65 * s + 0.20 * a + 0.15 * p
       END AS score
FROM componentes
ORDER BY score DESC, s DESC, id ASC
LIMIT 5
"""