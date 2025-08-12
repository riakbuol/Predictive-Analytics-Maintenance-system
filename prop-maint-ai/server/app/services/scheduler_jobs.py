from __future__ import annotations

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import MaintenanceRequest, MaintenanceStatus, User, UserRole, Assignment
from ..services.scheduling import generate_weekly_schedule
from ..services.prediction import engine_singleton


def run_nightly_predictions() -> None:
    db: Session = SessionLocal()
    try:
        # Here we simply call suggest via engine on all properties-like inputs handled elsewhere.
        # In a real setup, you might persist predictions or update priorities.
        # This stub demonstrates recurring job structure without heavy logic (already available in router).
        pass
    finally:
        db.close()


def run_weekly_assignment() -> None:
    db: Session = SessionLocal()
    try:
        staff = db.query(User).filter(User.role == UserRole.STAFF, User.is_active == True).all()
        staff_ids = [s.id for s in staff]
        pending = db.query(MaintenanceRequest).filter(MaintenanceRequest.status.in_([MaintenanceStatus.PENDING, MaintenanceStatus.ACTIVE])).all()
        tasks = [{"request_id": r.id, "priority": r.priority if r.priority is not None else 3} for r in pending]
        monday = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        plan = generate_weekly_schedule(tasks, staff_ids, monday)
        for item in plan:
            exists = db.query(Assignment).filter(Assignment.request_id == item["request_id"]).first()
            if exists:
                continue
            db.add(Assignment(request_id=item["request_id"], staff_id=item["staff_id"], scheduled_for=item["scheduled_for"], status="scheduled"))
        db.commit()
    finally:
        db.close()


scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global scheduler
    if scheduler is not None and scheduler.running:
        return
    scheduler = BackgroundScheduler(timezone="UTC")
    # Nightly at 02:00 UTC
    scheduler.add_job(run_nightly_predictions, "cron", hour=2, minute=0, id="nightly_predictions", replace_existing=True)
    # Weekly Monday 03:00 UTC
    scheduler.add_job(run_weekly_assignment, "cron", day_of_week="mon", hour=3, minute=0, id="weekly_assignment", replace_existing=True)
    scheduler.start()


def shutdown_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None