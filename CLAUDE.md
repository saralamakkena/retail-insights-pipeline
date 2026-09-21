# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Retail Insights Pipeline is an end-to-end, cloud-agnostic batch ELT pipeline being built incrementally (~30 minutes/day): raw Olist e-commerce CSVs → Postgres → dbt staging/mart models (star schema) → Airflow orchestration → dashboard.

The project is at an early stage: `dbt/`, `airflow/dags/`, `docker/`, and `scripts/` currently only contain `.gitkeep` placeholders. Only the Postgres container and the raw CSV ingestion script exist so far. Expect to build out dbt models, Airflow DAGs, and dashboarding from scratch as the project progresses — don't assume conventions for those layers exist yet; establish them consistently with the ingestion script's style when you do.

## Stack

- **Ingestion:** Python (pandas, sqlalchemy, psycopg2)
- **Warehouse:** PostgreSQL (via Docker Compose)
- **Transformation:** dbt (dbt-postgres); PySpark planned later for one heavier job
- **Orchestration:** Apache Airflow (not yet implemented)
- **CI:** GitHub Actions (not yet implemented)
- **Dashboard:** Metabase or Streamlit (later, undecided)

## Commands

Start Postgres:
```bash
docker compose up -d
docker compose ps
```

Set up the Python environment:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Load raw CSVs into Postgres (requires Postgres running and `.env` configured):
```bash
python ingestion/load_raw.py
```

Connect to Postgres directly:
```bash
psql -h localhost -U retail_admin -d retail_insights   # password from .env
```

There are no test, lint, or build commands configured yet.

## Configuration

- Postgres connection settings (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`) are read from a `.env` file via `python-dotenv`, with fallback defaults (`retail_admin` / `retail_pw` / `retail_insights` / `localhost` / `5432`) defined independently in both `docker-compose.yml` and `ingestion/load_raw.py`. Keep these two in sync when changing defaults.
- Raw Olist CSVs (downloaded manually from Kaggle) live in `data/raw/` and are git-ignored; only `.gitkeep` is committed there.

## Architecture: ingestion

`ingestion/load_raw.py` is the only pipeline stage implemented so far. It:

1. Globs every `*.csv` in `data/raw/`.
2. Derives a Postgres table name from each filename by stripping the `olist_` prefix and `_dataset` suffix (e.g. `olist_order_items_dataset.csv` → `order_items`).
3. Loads each CSV into the `raw` schema (created if missing) in chunks of 5,000 rows via `pandas.read_sql`/`to_sql`, replacing the table on the first chunk and appending for the rest.

When extending ingestion (new sources, incremental loads, etc.), follow this same pattern: schema-qualified raw tables, filename-derived table names, chunked loads.
