# Retail Insights Pipeline

An end-to-end, cloud-agnostic batch ELT pipeline: raw e-commerce order data →
Postgres → dbt staging/mart models (star schema) → Airflow orchestration →
dashboard. Built incrementally, ~30 minutes a day.

Full day-by-day plan: see the project plan doc (linked in my notes / ask Claude).

## Stack

- **Ingestion:** Python (pandas)
- **Warehouse:** PostgreSQL
- **Transformation:** dbt (+ PySpark for one heavier job, later)
- **Orchestration:** Apache Airflow
- **Containers:** Docker Compose
- **CI:** GitHub Actions
- **Dashboard:** Metabase or Streamlit (later)

## Dataset

[Brazilian E-Commerce (Olist) dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
from Kaggle. Download the CSVs and place them in `data/raw/` (they're
git-ignored — see `.gitignore`).

## Getting started

1. Copy `.env.example` to `.env` and adjust values if you want.
2. Start Postgres:
   ```bash
   docker compose up -d
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Verify Postgres is reachable:
   ```bash
   docker compose ps
   psql -h localhost -U retail_admin -d retail_insights   # password from .env
   ```

## Project structure

```
retail-insights-pipeline/
├── docker-compose.yml      # Postgres (and later Airflow)
├── ingestion/              # Python scripts: raw CSVs -> Postgres
├── dbt/                    # dbt project: staging + mart models
├── airflow/dags/           # Airflow DAGs orchestrating the pipeline
├── scripts/                # One-off helper / validation scripts
└── data/raw/               # Downloaded CSVs (not committed)
```

## Progress log

| Date | What shipped |
| --- | --- |
| 2026-09-18 | Day 1: project scaffold, Docker Compose (Postgres), README |
| 2026-09-21 | Day 2: raw CSV ingestion (`ingestion/load_raw.py`) into `raw` schema |
| 2026-09-21 | Day 3: dbt project + staging views over all 9 raw tables |
