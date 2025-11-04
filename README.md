## InternHub Backend (FastAPI)

- FastAPI + SQLAlchemy (async) + Pydantic + JWT
- PostgreSQL connection via `DATABASE_URL`

Run locally:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment:
- `DATABASE_URL=postgresql+asyncpg://hub:hubpass@localhost:5433/hubdb_v2`
- Configure other flags in `.env`.

Alembic:
```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Health check: GET `/healthz`.

 
