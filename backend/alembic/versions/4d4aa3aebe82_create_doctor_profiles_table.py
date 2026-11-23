"""create doctor profiles table"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4d4aa3aebe82"
down_revision: Union[str, Sequence[str], None] = "6fbfc7e7212e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "doctor_profiles",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "specialization",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "qualification",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "medical_registration_number",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "years_of_experience",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "hospital_name",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "consultation_fee",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
        sa.Column(
            "bio",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "verification_status",
            sa.Enum(
                "pending",
                "verified",
                "rejected",
                name="doctor_verification_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_doctor_profiles_medical_registration_number",
        "doctor_profiles",
        ["medical_registration_number"],
        unique=True,
    )

    op.create_index(
        "ix_doctor_profiles_user_id",
        "doctor_profiles",
        ["user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_doctor_profiles_user_id",
        table_name="doctor_profiles",
    )

    op.drop_index(
        "ix_doctor_profiles_medical_registration_number",
        table_name="doctor_profiles",
    )

    op.drop_table("doctor_profiles")