# Predictive Maintenance System (Property Management)

A full-stack system for tenant maintenance reporting, predictive maintenance, task assignment, and administrative analytics. Backend is FastAPI with SQLAlchemy and JWT auth. Includes a pluggable ML prediction engine and CSV import/export.

## Features
- Tenant maintenance reporting with photos
- Prediction engine (RandomForest baseline) with training on uploaded CSV
- Task assignment and weekly scheduling
- Admin dashboard APIs: metrics, active/pending/predicted tasks
- Tenant feedback collection
- CSV import/export of maintenance data
- Role-based access control (tenant, staff, admin)

## Quickstart (Backend)

Requirements: Python 3.10+

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open API docs at: http://localhost:8000/docs

### Environment Variables
- `DATABASE_URL` (default: `sqlite:///./app.db`)
- `JWT_SECRET` (default: random dev secret)
- `JWT_EXPIRE_MINUTES` (default: 60)
- `ALLOWED_ORIGINS` (comma-separated; default: `*`)

### Initial Admin
- Register a tenant at `/auth/register`
- To create an admin or staff, use the `/admin/users` endpoints after logging in as admin, or set `ALLOW_OPEN_ADMIN_SIGNUP=true` for development mode and call `/auth/register` with role `admin`.

## CSV Schemas (for Training/Import)
- Training CSV expected columns (example minimal): `property_id,property_age,last_service_days,num_past_issues,season,humidity,temperature,category`
- Import CSV for maintenance requests: `tenant_email,property_name,category,urgency,description,timestamp`

## Project Structure
```
prop-maint-ai/
  server/
    app/
      routers/
      services/
      main.py
      models.py
      schemas.py
      database.py
      security.py
      config.py
    requirements.txt
```

## Next Steps
- Add React frontend (`web/`) consuming these APIs
- Add background workers for periodic predictions
- Swap SQLite for Postgres in production