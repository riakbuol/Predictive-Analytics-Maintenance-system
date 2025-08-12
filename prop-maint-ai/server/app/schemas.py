from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: Optional[str] = None  # tenant by default; admin/staff allowed only if configured


class UserOut(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True


class PropertyBase(BaseModel):
    name: str
    address: Optional[str] = None
    year_built: Optional[int] = None


class PropertyOut(PropertyBase):
    id: int

    class Config:
        from_attributes = True


class MaintenanceRequestCreate(BaseModel):
    property_id: int
    category: str
    urgency: str
    description: Optional[str] = None


class MaintenanceRequestOut(BaseModel):
    id: int
    tenant_id: int
    property_id: int
    category: str
    urgency: str
    description: Optional[str]
    photo_path: Optional[str]
    status: str
    priority: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    request_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    request_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    request_id: int
    staff_id: int
    scheduled_for: datetime


class AssignmentOut(BaseModel):
    id: int
    request_id: int
    staff_id: int
    scheduled_for: datetime
    status: str

    class Config:
        from_attributes = True


class MetricsOut(BaseModel):
    active_count: int
    pending_count: int
    predicted_count: int
    avg_resolution_hours: Optional[float]


class PredictionTrainStatus(BaseModel):
    message: str
    model_version: Optional[str] = None


class PredictionOut(BaseModel):
    property_id: int
    predicted_category: str
    severity: str
    priority: int
    predicted_for_date: datetime
    model_version: Optional[str] = None