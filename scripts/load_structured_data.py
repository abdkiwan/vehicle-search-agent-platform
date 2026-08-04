from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.environ["DATABASE_URL"]


def load_dealers(conn: psycopg.Connection) -> None:
    path = ROOT / "data" / "structured" / "dealers.csv"
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            conn.execute(
                """
                INSERT INTO dealers (
                    id, name, city, postal_code, country_code, rating,
                    is_verified, warranty_months, created_at
                ) VALUES (
                    %(id)s, %(name)s, %(city)s, %(postal_code)s,
                    %(country_code)s, %(rating)s, %(is_verified)s,
                    %(warranty_months)s, %(created_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    rating = EXCLUDED.rating,
                    is_verified = EXCLUDED.is_verified,
                    warranty_months = EXCLUDED.warranty_months
                """,
                row,
            )


def load_vehicles(conn: psycopg.Connection) -> None:
    path = ROOT / "data" / "structured" / "vehicles.csv"
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            values = dict(row)
            values["equipment"] = Jsonb(json.loads(row["equipment"]))
            conn.execute(
                """
                INSERT INTO vehicles (
                    id, dealer_id, make, model, variant, price_eur_cents,
                    year, mileage_km, fuel_type, transmission, body_type,
                    power_kw, color, equipment, description, status, created_at
                ) VALUES (
                    %(id)s, %(dealer_id)s, %(make)s, %(model)s, %(variant)s,
                    %(price_eur_cents)s, %(year)s, %(mileage_km)s,
                    %(fuel_type)s, %(transmission)s, %(body_type)s,
                    %(power_kw)s, %(color)s, %(equipment)s, %(description)s,
                    %(status)s, %(created_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    price_eur_cents = EXCLUDED.price_eur_cents,
                    mileage_km = EXCLUDED.mileage_km,
                    equipment = EXCLUDED.equipment,
                    description = EXCLUDED.description,
                    status = EXCLUDED.status
                """,
                values,
            )


def main() -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        load_dealers(conn)
        load_vehicles(conn)
        conn.commit()
        dealer_count = conn.execute("SELECT COUNT(*) FROM dealers").fetchone()[0]
        vehicle_count = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
        print(f"Loaded {dealer_count} dealers and {vehicle_count} vehicles.")


if __name__ == "__main__":
    main()
