from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.patient_profile import PatientProfile
from models.user import User, UserRole
from schemas.patient_profile import (
    PatientProfileCreate,
    PatientProfileResponse,
    PatientProfileUpdate,
)
from services.auth import get_current_user


router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)


def require_patient(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required",
        )

    return current_user


@router.post(
    "/me/profile",
    response_model=PatientProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_profile(
    profile_data: PatientProfileCreate,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db),
):
    existing_profile = db.scalar(
        select(PatientProfile).where(
            PatientProfile.user_id == current_user.id
        )
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient profile already exists",
        )

    profile = PatientProfile(
        user_id=current_user.id,
        **profile_data.model_dump(),
    )

    db.add(profile)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(profile)

    return profile


@router.get(
    "/me/profile",
    response_model=PatientProfileResponse,
)
def get_my_profile(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(PatientProfile).where(
            PatientProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    return profile


@router.put(
    "/me/profile",
    response_model=PatientProfileResponse,
)
def update_my_profile(
    profile_data: PatientProfileUpdate,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(PatientProfile).where(
            PatientProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(profile, field, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(profile)

    return profile