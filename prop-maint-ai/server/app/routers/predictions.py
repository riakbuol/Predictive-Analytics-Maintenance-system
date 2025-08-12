from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import MaintenanceRequest, MaintenanceStatus, Prediction, Property, User
from ..security import require_role
from ..services.prediction import engine_singleton

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/train", response_model=schemas.PredictionTrainStatus)
async def train_model(csv: UploadFile = File(...), _: User = Depends(require_role("admin"))):
    import os, tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await csv.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = engine_singleton.train_from_csv(tmp_path)
        return schemas.PredictionTrainStatus(message="trained", model_version=result.get("version"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@router.post("/suggest", response_model=List[schemas.PredictionOut])
def suggest_predictions(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    # Create synthetic feature rows based on properties and recent issues
    props = db.query(Property).all()
    rows = []
    for p in props:
        property_age = (datetime.utcnow().year - (p.year_built or datetime.utcnow().year))
        last_service_days = 90
        num_past_issues = db.query(MaintenanceRequest).filter(MaintenanceRequest.property_id == p.id).count()
        season = 2
        humidity = 50
        temperature = 24
        rows.append({
            "property_age": property_age,
            "last_service_days": last_service_days,
            "num_past_issues": num_past_issues,
            "season": season,
            "humidity": humidity,
            "temperature": temperature,
        })

    preds = engine_singleton.predict(rows)

    out: List[schemas.PredictionOut] = []
    for p, pr in zip(props, preds):
        pred = Prediction(
            property_id=p.id,
            predicted_category=pr["predicted_category"],
            severity=pr["severity"],
            priority=pr["priority"],
            predicted_for_date=datetime.utcnow(),
            model_version=engine_singleton.model_version,
        )
        db.add(pred)
        db.commit()

        out.append(schemas.PredictionOut(
            property_id=p.id,
            predicted_category=pred.predicted_category,
            severity=pred.severity,
            priority=pred.priority,
            predicted_for_date=pred.predicted_for_date,
            model_version=pred.model_version,
        ))
    return out


@router.post("/apply-priorities")
def apply_predicted_priorities(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    # Update pending tasks' priority from latest predictions by property and category
    preds = db.query(Prediction).order_by(Prediction.predicted_for_date.desc()).all()
    for pr in preds:
        q = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.property_id == pr.property_id,
            MaintenanceRequest.category.ilike(f"%{pr.predicted_category}%"),
            MaintenanceRequest.status.in_([MaintenanceStatus.PENDING, MaintenanceStatus.ACTIVE]),
        )
        for req in q.all():
            req.priority = pr.priority
    db.commit()
    return {"message": "applied"}