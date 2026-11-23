import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: uuid.UUID
    appointment_at: datetime

    reason: str | None = Field(
        default=None,
        max_length=1000,
    )


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_at: datetime
    reason: str | None
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime