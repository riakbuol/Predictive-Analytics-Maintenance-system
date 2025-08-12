from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import (
    User,
    UserRole,
    MaintenanceRequest,
    MaintenanceStatus,
    Assignment,
    Property,
)
from ..security import require_role, hash_password
from ..services.scheduling import generate_weekly_schedule

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/tasks", response_model=List[schemas.MaintenanceRequestOut])
def list_tasks(status: str = "pending", db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    q = db.query(MaintenanceRequest)
    if status:
        q = q.filter(MaintenanceRequest.status == status)
    return q.order_by(MaintenanceRequest.created_at.desc()).all()


@router.get("/tasks/all", response_model=List[schemas.MaintenanceRequestOut])
def list_all_tasks(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    return db.query(MaintenanceRequest).order_by(MaintenanceRequest.created_at.desc()).all()


@router.patch("/tasks/{request_id}", response_model=schemas.MaintenanceRequestOut)
def update_task(request_id: int, payload: schemas.MaintenanceRequestUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    if payload.status is not None:
        req.status = payload.status
    if payload.priority is not None:
        req.priority = payload.priority
    if payload.category is not None:
        req.category = payload.category
    if payload.urgency is not None:
        req.urgency = payload.urgency
    if payload.description is not None:
        req.description = payload.description
    req.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(req)
    return req


@router.post("/assign", response_model=List[schemas.AssignmentOut])
def assign_tasks(db: Session = Depends(get_db), admin: User = Depends(require_role("admin"))):
    staff = db.query(User).filter(User.role == UserRole.STAFF, User.is_active == True).all()
    staff_ids = [s.id for s in staff]

    if not staff_ids:
        raise HTTPException(status_code=400, detail="No staff available")

    pending = (
        db.query(MaintenanceRequest)
        .filter(MaintenanceRequest.status.in_([MaintenanceStatus.PENDING, MaintenanceStatus.ACTIVE]))
        .all()
    )

    tasks = [
        {"request_id": r.id, "priority": r.priority if r.priority is not None else 3}
        for r in pending
    ]

    monday = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    plan = generate_weekly_schedule(tasks, staff_ids, monday)

    assignments: List[Assignment] = []
    for item in plan:
        existing = db.query(Assignment).filter(Assignment.request_id == item["request_id"]).first()
        if existing:
            continue
        a = Assignment(
            request_id=item["request_id"],
            staff_id=item["staff_id"],
            scheduled_for=item["scheduled_for"],
            status="scheduled",
        )
        assignments.append(a)
        db.add(a)

    db.commit()
    for a in assignments:
        db.refresh(a)
    return assignments


@router.get("/metrics", response_model=schemas.MetricsOut)
def metrics(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    active = db.query(MaintenanceRequest).filter(MaintenanceRequest.status == MaintenanceStatus.ACTIVE).count()
    pending = db.query(MaintenanceRequest).filter(MaintenanceRequest.status == MaintenanceStatus.PENDING).count()
    predicted = db.query(MaintenanceRequest).filter(MaintenanceRequest.status == MaintenanceStatus.PREDICTED).count()

    # Placeholder: resolution time requires historical closed timestamps
    avg_resolution_hours = None
    return schemas.MetricsOut(
        active_count=active,
        pending_count=pending,
        predicted_count=predicted,
        avg_resolution_hours=avg_resolution_hours,
    )


@router.post("/properties", response_model=schemas.PropertyOut)
def create_property(payload: schemas.PropertyBase, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    if db.query(Property).filter(Property.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Property already exists")
    p = Property(name=payload.name, address=payload.address, year_built=payload.year_built)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/properties", response_model=List[schemas.PropertyOut])
def list_properties(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    return db.query(Property).all()


@router.post("/users/staff", response_model=schemas.UserOut)
def create_staff(user: schemas.UserCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(email=user.email, full_name=user.full_name, password_hash=hash_password(user.password), role=UserRole.STAFF)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u