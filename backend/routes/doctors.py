from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.doctor_profile import DoctorProfile
from models.user import User
from schemas.doctor_profile import (
    DoctorProfileCreate,
    DoctorProfileResponse,
    DoctorProfileUpdate,
)
from services.roles import require_doctor


router = APIRouter(
    prefix="/api/doctors",
    tags=["Doctors"],
)


@router.post(
    "/me/profile",
    response_model=DoctorProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    data: DoctorProfileCreate,
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(DoctorProfile).where(
            DoctorProfile.user_id == user.id
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Doctor profile already exists",
        )

    registration_exists = db.scalar(
        select(DoctorProfile).where(
            DoctorProfile.medical_registration_number
            == data.medical_registration_number
        )
    )

    if registration_exists:
        raise HTTPException(
            status_code=409,
            detail="Medical registration number already exists",
        )

    profile = DoctorProfile(
        user_id=user.id,
        **data.model_dump(),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get(
    "/me/profile",
    response_model=DoctorProfileResponse,
)
def get_profile(
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(DoctorProfile).where(
            DoctorProfile.user_id == user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found",
        )

    return profile


@router.put(
    "/me/profile",
    response_model=DoctorProfileResponse,
)
def update_profile(
    data: DoctorProfileUpdate,
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(DoctorProfile).where(
            DoctorProfile.user_id == user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found",
        )

    for field, value in data.model_dump(
        exclude_unset=True
    ).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile