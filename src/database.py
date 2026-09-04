"""Constrói o banco SQLite analítico a partir dos CSVs processados."""

from __future__ import annotations

import sqlite3

import pandas as pd

from .config import DATABASE, DATA_PROCESSED, ROOT


def build_database(database_path=DATABASE) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    transactions = pd.read_csv(DATA_PROCESSED / "transactions_scored.csv")
    rule_summary = pd.read_csv(DATA_PROCESSED / "rule_summary.csv")
    monthly = pd.read_csv(DATA_PROCESSED / "monthly_monitoring.csv")
    with sqlite3.connect(database_path) as connection:
        connection.executescript((ROOT / "database" / "schema.sql").read_text(encoding="utf-8"))
        transactions.to_sql("transactions_scored", connection, if_exists="append", index=False)
        rule_summary.to_sql("rule_summary", connection, if_exists="append", index=False)
        monthly.to_sql("monthly_monitoring", connection, if_exists="append", index=False)
        connection.executescript((ROOT / "database" / "views.sql").read_text(encoding="utf-8"))
    print(f"Banco criado em {database_path}")


if __name__ == "__main__":
    build_database()
