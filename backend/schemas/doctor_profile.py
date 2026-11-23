import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.doctor_profile import VerificationStatus


class DoctorProfileCreate(BaseModel):
    specialization: str = Field(min_length=2, max_length=150)
    qualification: str = Field(min_length=2, max_length=255)
    medical_registration_number: str = Field(
        min_length=3,
        max_length=100,
    )
    years_of_experience: int | None = Field(
        default=None,
        ge=0,
        le=80,
    )
    hospital_name: str | None = Field(
        default=None,
        max_length=255,
    )
    consultation_fee: Decimal | None = Field(
        default=None,
        ge=0,
    )
    bio: str | None = None


class DoctorProfileUpdate(BaseModel):
    specialization: str | None = Field(
        default=None,
        max_length=150,
    )
    qualification: str | None = Field(
        default=None,
        max_length=255,
    )
    years_of_experience: int | None = Field(
        default=None,
        ge=0,
        le=80,
    )
    hospital_name: str | None = Field(
        default=None,
        max_length=255,
    )
    consultation_fee: Decimal | None = Field(
        default=None,
        ge=0,
    )
    bio: str | None = None


class DoctorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    specialization: str
    qualification: str
    medical_registration_number: str
    years_of_experience: int | None
    hospital_name: str | None
    consultation_fee: Decimal | None
    bio: str | None
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime
