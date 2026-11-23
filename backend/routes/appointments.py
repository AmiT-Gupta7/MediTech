from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from database import get_db
from models.appointment import Appointment, AppointmentStatus
from models.doctor_profile import DoctorProfile, VerificationStatus
from models.user import User, UserRole
from schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
)
from services.auth import get_current_user


router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"],
)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments",
        )

    doctor = db.get(
        User,
        data.doctor_id,
    )

    if not doctor or doctor.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    doctor_profile = db.scalar(
        select(DoctorProfile).where(
            DoctorProfile.user_id == doctor.id
        )
    )

    if not doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor profile is incomplete",
        )

    if (
        doctor_profile.verification_status
        != VerificationStatus.VERIFIED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is not verified",
        )

    appointment_time = data.appointment_at

    if appointment_time.tzinfo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment time must include timezone",
        )

    if appointment_time <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment must be scheduled in the future",
        )

    existing = db.scalar(
        select(Appointment).where(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_at == appointment_time,
            Appointment.status == AppointmentStatus.BOOKED,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Doctor already has an appointment at this time",
        )

    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor.id,
        appointment_at=appointment_time,
        reason=data.reason,
        status=AppointmentStatus.BOOKED,
    )

    db.add(appointment)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(appointment)

    return appointment


@router.get(
    "/me",
    response_model=list[AppointmentResponse],
)
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Appointment)

    if current_user.role == UserRole.PATIENT:
        query = query.where(
            Appointment.patient_id == current_user.id
        )

    elif current_user.role == UserRole.DOCTOR:
        query = query.where(
            Appointment.doctor_id == current_user.id
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Appointment access denied",
        )

    query = query.order_by(
        Appointment.appointment_at
    )

    return list(
        db.scalars(query).all()
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointment = db.get(
        Appointment,
        appointment_id,
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    allowed = (
        appointment.patient_id == current_user.id
        or
        appointment.doctor_id == current_user.id
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Appointment access denied",
        )

    return appointment


@router.put(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointment = db.get(
        Appointment,
        appointment_id,
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    if appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the patient can cancel this appointment",
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment is already cancelled",
        )

    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Completed appointments cannot be cancelled",
        )

    appointment.status = AppointmentStatus.CANCELLED

    db.commit()
    db.refresh(appointment)

    return appointment


@router.put(
    "/{appointment_id}/complete",
    response_model=AppointmentResponse,
)
def complete_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointment = db.get(
        Appointment,
        appointment_id,
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    # Only the doctor assigned to this appointment can complete it
    if appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned doctor can complete this appointment",
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled appointments cannot be completed",
        )

    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment is already completed",
        )

    appointment.status = AppointmentStatus.COMPLETED

    db.commit()
    db.refresh(appointment)

    return appointment