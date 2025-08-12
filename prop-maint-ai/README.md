# Predictive Maintenance System (Property Management)

A full-stack system for tenant maintenance reporting, predictive maintenance, task assignment, and administrative analytics. Backend is FastAPI with SQLAlchemy and JWT auth. Includes a pluggable ML prediction engine and CSV import/export.

## Features
- Tenant maintenance reporting with photos
- Prediction engine (RandomForest baseline) with training on uploaded CSV
- Task assignment and weekly scheduling (APScheduler jobs)
- Admin dashboard APIs: metrics, active/pending/predicted tasks
- Tenant feedback collection
- CSV import/export of maintenance data
- Role-based access control (tenant, staff, admin)
- Static HTML/CSS UI served at `/app`

## Quickstart (Backend)

Requirements: Python 3.10+

```bash
cd server
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir app --reload
```

Open API docs at: http://localhost:8000/docs
UI: http://localhost:8000/app

### Database (MySQL)
- Default `DATABASE_URL` is `mysql+pymysql://root:password@localhost:3306/prop_maint`
- Override via env: `export DATABASE_URL="mysql+pymysql://USER:PASS@HOST:3306/DBNAME"`
- For local dev without MySQL, set SQLite: `export DATABASE_URL="sqlite:///./app.db"`

### Storage
- `STORAGE_BACKEND`: `local` (default) or `s3`
- Local: `LOCAL_UPLOAD_DIR` (default `uploads/`)
- S3: `AWS_REGION`, `S3_BUCKET`, `S3_PREFIX` (optional), `S3_ENDPOINT_URL` (optional for MinIO)

### Environment Variables
- `DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `ALLOWED_ORIGINS`, `ALLOW_OPEN_ADMIN_SIGNUP`

### Scheduler
- Nightly predictions stub (02:00 UTC), weekly assignment (Mon 03:00 UTC)

### Alembic Migrations
```bash
cd server
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### Docker
- Compose (MySQL + API):
```bash
docker compose up -d
```
- Dockerfile build:
```bash
docker build -t prop-maint-ai .
docker run -p 8000:8000 --env DATABASE_URL="mysql+pymysql://root:devpass@host.docker.internal:3306/prop_maint" prop-maint-ai
```

### Tests
```bash
cd server
pytest -q
```

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
      static_frontend/
      main.py
      models.py
      schemas.py
      database.py
      security.py
      config.py
    requirements.txt
```

## Frontend (Static HTML/CSS)
- Served at `/app`
- Uses minimal JavaScript to call the API
