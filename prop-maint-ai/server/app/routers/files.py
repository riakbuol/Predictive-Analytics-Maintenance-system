import csv
import io
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import MaintenanceRequest, Property, User, MaintenanceStatus
from ..security import require_role, hash_password

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/import")
async def import_requests(csv_file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    content = await csv_file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    count = 0
    for row in reader:
        property_name = row.get("property_name")
        prop = db.query(Property).filter(Property.name == property_name).first()
        if not prop:
            prop = Property(name=property_name)
            db.add(prop)
            db.commit()
            db.refresh(prop)

        tenant_email = row.get("tenant_email") or f"tenant_{prop.id}@example.com"
        tenant = db.query(User).filter(User.email == tenant_email).first()
        if not tenant:
            tenant = User(email=tenant_email, password_hash=hash_password("Temp1234!"), role="tenant", full_name=None)
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        req = MaintenanceRequest(
            tenant_id=tenant.id,
            property_id=prop.id,
            category=row.get("category") or "general",
            urgency=row.get("urgency") or "medium",
            description=row.get("description"),
            status=row.get("status") or MaintenanceStatus.PENDING,
        )
        db.add(req)
        count += 1
    db.commit()
    return {"imported": count}


@router.get("/export/requests")
def export_requests(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    q = db.query(MaintenanceRequest).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "tenant_id", "property_id", "category", "urgency", "description", "status", "priority", "created_at"
    ])
    for r in q:
        writer.writerow([
            r.id, r.tenant_id, r.property_id, r.category, r.urgency, r.description or "", r.status, r.priority or "", r.created_at.isoformat()
        ])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=maintenance_requests.csv"
    })