from datetime import date

from sqlalchemy import event, select

from app import db
from app.models.Base import BaseModel


class Demographics(BaseModel):
    __tablename__ = "demographics"

    birthDate = db.Column(db.Date, nullable=True)
    sex = db.Column(
        db.Enum("male", "female", name="demographics_sex", native_enum=False),
        nullable=True,
    )
    americanIndianOrAlaskaNative = db.Column(
        db.Enum("true", "false", name="demographics_american_indian", native_enum=False),
        nullable=True,
    )
    asian = db.Column(
        db.Enum("true", "false", name="demographics_asian", native_enum=False),
        nullable=True,
    )
    blackOrAfricanAmerican = db.Column(
        db.Enum("true", "false", name="demographics_black", native_enum=False),
        nullable=True,
    )
    nativeHawaiianOrOtherPacificIslander = db.Column(
        db.Enum("true", "false", name="demographics_native_hawaiian", native_enum=False),
        nullable=True,
    )
    white = db.Column(
        db.Enum("true", "false", name="demographics_white", native_enum=False),
        nullable=True,
    )
    demographicRaceTwoOrMoreRaces = db.Column(
        db.Enum("true", "false", name="demographics_two_or_more", native_enum=False),
        nullable=True,
    )
    hispanicOrLatinoEthnicity = db.Column(
        db.Enum("true", "false", name="demographics_hispanic", native_enum=False),
        nullable=True,
    )
    countryOfBirthCode = db.Column(db.String(255), nullable=True)
    stateOfBirthAbbreviation = db.Column(db.String(10), nullable=True)
    cityOfBirth = db.Column(db.String(255), nullable=True)
    publicSchoolResidenceStatus = db.Column(db.String(255), nullable=True)

    def to_dict(self) -> dict:
        payload = super().to_dict()

        if isinstance(payload.get("birthDate"), date):
            payload["birthDate"] = payload["birthDate"].isoformat()

        return payload


@event.listens_for(Demographics, "before_insert")
@event.listens_for(Demographics, "before_update")
def validate_demographics_rules(mapper, connection, target: Demographics) -> None:
    from app.models.User import User

    users = User.__table__

    if not target.sourcedId:
        raise ValueError("Demographics sourcedId must match an existing user sourcedId")

    if connection.execute(
        select(users.c.sourcedId).where(users.c.sourcedId == target.sourcedId),
    ).scalar_one_or_none() is None:
        raise ValueError("Demographics sourcedId must match an existing user sourcedId")
