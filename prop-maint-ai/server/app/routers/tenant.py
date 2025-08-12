from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import MaintenanceRequest, Feedback, Property, User, MaintenanceStatus
from ..security import require_role

router = APIRouter(prefix="/tenant", tags=["tenant"])


@router.post("/requests", response_model=schemas.MaintenanceRequestOut)
async def create_request(
    property_id: int = Form(...),
    category: str = Form(...),
    urgency: str = Form(...),
    description: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("tenant")),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    photo_path = None
    if photo is not None:
        uploads_dir = "uploads"
        import os
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{photo.filename}"
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as f:
            f.write(await photo.read())
        photo_path = file_path

    req = MaintenanceRequest(
        tenant_id=user.id,
        property_id=property_id,
        category=category,
        urgency=urgency,
        description=description,
        photo_path=photo_path,
        status=MaintenanceStatus.PENDING,
        priority=None,
        updated_at=datetime.utcnow(),
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/requests", response_model=List[schemas.MaintenanceRequestOut])
def list_my_requests(db: Session = Depends(get_db), user: User = Depends(require_role("tenant"))):
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.tenant_id == user.id).order_by(MaintenanceRequest.created_at.desc()).all()


@router.post("/feedback", response_model=schemas.FeedbackOut)
def submit_feedback(payload: schemas.FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(require_role("tenant"))):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == payload.request_id).first()
    if not req or req.tenant_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")

    fb = Feedback(request_id=req.id, rating=payload.rating, comment=payload.comment)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/properties", response_model=List[schemas.PropertyOut])
def list_properties(db: Session = Depends(get_db), user: User = Depends(require_role("tenant"))):
    return db.query(Property).all()