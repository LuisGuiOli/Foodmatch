import csv
import os
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "data" / "catalogo_demo.csv"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://foodmatch:foodmatch_dev@127.0.0.1:5433/foodmatch",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    rating NUMERIC(2, 1) NOT NULL CHECK (rating BETWEEN 1 AND 5),
    city TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    embedding VECTOR(384)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    dish_id INTEGER NOT NULL REFERENCES dishes(id),
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL
);
"""

UPSERT_RESTAURANT = """
INSERT INTO restaurants (id, name, description, rating, city)
VALUES (%(restaurant_id)s, %(restaurant_name)s, %(restaurant_description)s,
        %(restaurant_rating)s, %(city)s)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    rating = EXCLUDED.rating,
    city = EXCLUDED.city
"""

UPSERT_DISH = """
INSERT INTO dishes (id, restaurant_id, name, description, category, price)
VALUES (%(dish_id)s, %(restaurant_id)s, %(dish_name)s, %(dish_description)s,
        %(category)s, %(price)s)
ON CONFLICT (id) DO UPDATE SET
    restaurant_id = EXCLUDED.restaurant_id,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    price = EXCLUDED.price,
    embedding = CASE
        WHEN (dishes.name, dishes.description, dishes.category)
             IS DISTINCT FROM (EXCLUDED.name, EXCLUDED.description, EXCLUDED.category)
        THEN NULL
        ELSE dishes.embedding
    END
"""

UPSERT_REVIEW = """
INSERT INTO reviews (id, dish_id, rating, comment)
VALUES (%(review_id)s, %(dish_id)s, %(review_rating)s, %(review_comment)s)
ON CONFLICT (id) DO UPDATE SET
    dish_id = EXCLUDED.dish_id,
    rating = EXCLUDED.rating,
    comment = EXCLUDED.comment
"""


def main() -> None:
    with CATALOG_PATH.open(encoding="utf-8", newline="") as catalog:
        with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
            conn.execute(SCHEMA)

            for row in csv.DictReader(catalog):
                conn.execute(UPSERT_RESTAURANT, row)
                conn.execute(UPSERT_DISH, row)
                if row["review_id"]:
                    conn.execute(UPSERT_REVIEW, row)

    print("Carga do catálogo concluída.")


if __name__ == "__main__":
    main()