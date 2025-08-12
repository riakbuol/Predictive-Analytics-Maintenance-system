from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional

from .database import Base


class UserRole:
    TENANT = "tenant"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default=UserRole.TENANT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    year_built: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        back_populates="property"
    )


class MaintenanceStatus:
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    PREDICTED = "predicted"


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))

    category: Mapped[str] = mapped_column(String(100))
    urgency: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    photo_path: Mapped[Optional[str]] = mapped_column(String(255))

    status: Mapped[str] = mapped_column(String(50), default=MaintenanceStatus.PENDING)
    priority: Mapped[Optional[int]] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tenant: Mapped[User] = relationship("User", back_populates="maintenance_requests")
    property: Mapped[Property] = relationship("Property", back_populates="maintenance_requests")
    feedback: Mapped[Optional["Feedback"]] = relationship("Feedback", back_populates="request", uselist=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id"), unique=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped[MaintenanceRequest] = relationship("MaintenanceRequest", back_populates="feedback")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    predicted_category: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(50))
    priority: Mapped[int] = mapped_column(Integer, default=3)
    predicted_for_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    model_version: Mapped[Optional[str]] = mapped_column(String(50))


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id"), unique=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scheduled_for: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="scheduled")