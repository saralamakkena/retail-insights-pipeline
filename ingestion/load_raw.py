import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "retail_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "retail_pw")
POSTGRES_DB = os.getenv("POSTGRES_DB", "retail_insights")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_SCHEMA = "raw"
CHUNK_SIZE = 5000


def table_name_from_filename(filename: str) -> str:
    """olist_order_items_dataset.csv -> order_items"""
    name = filename.replace(".csv", "")
    name = name.replace("olist_", "").replace("_dataset", "")
    return name


def get_engine():
    url = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    return create_engine(url)


def load_csv_to_table(engine, csv_path: Path) -> tuple[str, int]:
    table = table_name_from_filename(csv_path.name)
    print(f"Loading {csv_path.name} -> {RAW_SCHEMA}.{table} ...")

    row_count = 0
    for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=CHUNK_SIZE)):
        chunk.to_sql(
            table,
            engine,
            schema=RAW_SCHEMA,
            if_exists="replace" if i == 0 else "append",
            index=False,
        )
        row_count += len(chunk)

    print(f"  -> {row_count} rows loaded into {RAW_SCHEMA}.{table}")
    return table, row_count


def main():
    if not RAW_DATA_DIR.exists():
        sys.exit(f"Raw data folder not found: {RAW_DATA_DIR}")

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    if not csv_files:
        sys.exit(
            f"No CSV files found in {RAW_DATA_DIR}.\n"
            "Download the Olist dataset from Kaggle and place the CSVs there first: "
            "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
        )

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}"))

    summary = []
    for csv_path in csv_files:
        table, rows = load_csv_to_table(engine, csv_path)
        summary.append((table, rows))

    print("\nDone. Tables loaded:")
    for table, rows in summary:
        print(f"  {RAW_SCHEMA}.{table}: {rows} rows")


if __name__ == "__main__":
    main()
