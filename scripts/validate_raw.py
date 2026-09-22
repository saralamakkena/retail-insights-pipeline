import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "retail_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "retail_pw")
POSTGRES_DB = os.getenv("POSTGRES_DB", "retail_insights")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

RAW_SCHEMA = "raw"
NULL_WARNING_THRESHOLD = 5.0  # percent


def get_engine():
    url = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    return create_engine(url)


def get_raw_tables(engine) -> list[str]:
    inspector = inspect(engine)
    return sorted(inspector.get_table_names(schema=RAW_SCHEMA))


def get_row_count(engine, table: str) -> int:
    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {RAW_SCHEMA}."{table}"'))
        return result.scalar_one()


def get_null_rates(engine, table: str, row_count: int) -> dict:
    if row_count == 0:
        return {}

    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table, schema=RAW_SCHEMA)]

    # One query that counts nulls for every column at once, rather than
    # one round trip per column.
    null_counts_sql = ", ".join(
        f'COUNT(*) FILTER (WHERE "{col}" IS NULL) AS "{col}"' for col in columns
    )
    query = text(f'SELECT {null_counts_sql} FROM {RAW_SCHEMA}."{table}"')

    with engine.connect() as conn:
        row = conn.execute(query).mappings().one()

    return {col: (row[col] / row_count) * 100 for col in columns}


def main():
    engine = get_engine()
    tables = get_raw_tables(engine)

    if not tables:
        print(f"No tables found in schema '{RAW_SCHEMA}'. Run ingestion/load_raw.py first.")
        return

    print(f"Validating {len(tables)} tables in schema '{RAW_SCHEMA}'...\n")

    any_warnings = False
    for table in tables:
        row_count = get_row_count(engine, table)
        print(f"{RAW_SCHEMA}.{table}: {row_count} rows")

        null_rates = get_null_rates(engine, table, row_count)
        flagged = {col: rate for col, rate in null_rates.items() if rate > NULL_WARNING_THRESHOLD}

        if flagged:
            any_warnings = True
            for col, rate in sorted(flagged.items(), key=lambda item: -item[1]):
                print(f"    WARNING: {col} is {rate:.1f}% null")
        print()

    if not any_warnings:
        print(f"All columns are under the {NULL_WARNING_THRESHOLD}% null threshold.")


if __name__ == "__main__":
    main()
