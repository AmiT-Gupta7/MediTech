import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PatientProfileCreate(BaseModel):
    date_of_birth: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=50,
    )

    blood_group: str | None = Field(
        default=None,
        max_length=10,
    )

    height_cm: Decimal | None = Field(
        default=None,
        gt=0,
        le=300,
    )

    weight_kg: Decimal | None = Field(
        default=None,
        gt=0,
        le=500,
    )

    allergies: str | None = None
    medical_conditions: str | None = None

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )


class PatientProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=50)
    blood_group: str | None = Field(default=None, max_length=10)

    height_cm: Decimal | None = Field(
        default=None,
        gt=0,
        le=300,
    )

    weight_kg: Decimal | None = Field(
        default=None,
        gt=0,
        le=500,
    )

    allergies: str | None = None
    medical_conditions: str | None = None

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )


class PatientProfileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    user_id: uuid.UUID

    date_of_birth: date | None
    gender: str | None
    blood_group: str | None

    height_cm: Decimal | None
    weight_kg: Decimal | None

    allergies: str | None
    medical_conditions: str | None

    emergency_contact_name: str | None
    emergency_contact_phone: str | None

    created_at: datetime
    updated_at: datetime