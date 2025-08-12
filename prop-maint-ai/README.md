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
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir app --reload
```

Open API docs at: http://localhost:8000/docs

### Database (MySQL)
- Default `DATABASE_URL` is `mysql+pymysql://root:password@localhost:3306/prop_maint`
- Override via env: `export DATABASE_URL="mysql+pymysql://USER:PASS@HOST:3306/DBNAME"`
- For local dev without MySQL, set SQLite: `export DATABASE_URL="sqlite:///./app.db"`

### Environment Variables
- `DATABASE_URL` (default: MySQL DSN)
- `JWT_SECRET` (default: random dev secret)
- `JWT_EXPIRE_MINUTES` (default: 60)
- `ALLOWED_ORIGINS` (comma-separated; default: `*`)
- `ALLOW_OPEN_ADMIN_SIGNUP` (default: false)

### Initial Admin
- For dev: `export ALLOW_OPEN_ADMIN_SIGNUP=true` then call `/auth/register` with role `admin`
- Or register tenant then create staff via `/admin/users/staff`

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
