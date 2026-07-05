import json
from datetime import date

from sqlalchemy import event, select

from app import db
from app.models.Base import BaseModel


class Enrollment(BaseModel):
    __tablename__ = "enrollments"

    userSourcedId = db.Column(db.String(255), nullable=False)
    classSourcedId = db.Column(db.String(255), nullable=False)
    schoolSourcedId = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum(
            "administrator",
            "proctor",
            "student",
            "teacher",
            name="enrollment_role",
            native_enum=False,
        ),
        nullable=False,
    )
    primary = db.Column(
        db.Enum("true", "false", name="enrollment_primary", native_enum=False),
        nullable=True,
    )
    beginDate = db.Column(db.Date, nullable=True)
    endDate = db.Column(db.Date, nullable=True)

    __table_args__ = BaseModel.__table_args__ + (
        db.CheckConstraint(
            "primary IS NULL OR role = 'teacher'",
            name="ck_enrollment_primary_teacher_only",
        ),
    )

    @property
    def user(self) -> dict:
        return {
            "href": f"/users/{self.userSourcedId}",
            "sourcedId": self.userSourcedId,
            "type": "user",
        }

    @property
    def school(self) -> dict:
        return {
            "href": f"/schools/{self.schoolSourcedId}",
            "sourcedId": self.schoolSourcedId,
            "type": "org",
        }

    def to_dict(self) -> dict:
        payload = super().to_dict()
        payload.pop("userSourcedId", None)
        payload.pop("classSourcedId", None)
        payload.pop("schoolSourcedId", None)

        if isinstance(payload.get("beginDate"), date):
            payload["beginDate"] = payload["beginDate"].isoformat()

        if isinstance(payload.get("endDate"), date):
            payload["endDate"] = payload["endDate"].isoformat()

        payload["user"] = self.user
        payload["class"] = getattr(self, "class")
        payload["school"] = self.school
        return payload

    def class_guid_ref(self) -> dict:
        return {
            "href": f"/classes/{self.classSourcedId}",
            "sourcedId": self.classSourcedId,
            "type": "class",
        }

    locals()["class"] = property(class_guid_ref)


def _enrollment_ranges_overlap(
    existing_begin: date | None,
    existing_end: date | None,
    target_begin: date | None,
    target_end: date | None,
) -> bool:
    existing_begin = existing_begin or date.min
    existing_end = existing_end or date.max
    target_begin = target_begin or date.min
    target_end = target_end or date.max
    return existing_begin <= target_end and target_begin <= existing_end


def _enrollment_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


@event.listens_for(Enrollment, "before_insert")
@event.listens_for(Enrollment, "before_update")
def validate_primary_teacher_overlap(mapper, connection, target: Enrollment) -> None:
    from app.models.AcademicSessions import AcademicSession
    from app.models.Class import Class
    from app.models.Org import Org
    from app.models.User import User

    users = User.__table__
    classes = Class.__table__
    orgs = Org.__table__
    sessions = AcademicSession.__table__

    user_role = connection.execute(
        select(users.c.role).where(users.c.sourcedId == target.userSourcedId),
    ).scalar_one_or_none()
    if user_role is None:
        raise ValueError("enrollment user must reference an existing user")

    class_row = connection.execute(
        select(classes.c.schoolSourcedId, classes.c.termSourcedIds).where(classes.c.sourcedId == target.classSourcedId),
    ).first()
    if class_row is None:
        raise ValueError("enrollment class must reference an existing class")

    school_type = connection.execute(
        select(orgs.c.type).where(orgs.c.sourcedId == target.schoolSourcedId),
    ).scalar_one_or_none()
    if school_type != "school":
        raise ValueError("enrollment school must reference an org of type school")

    if class_row.schoolSourcedId != target.schoolSourcedId:
        raise ValueError("enrollment school must match the class school")

    if target.beginDate and target.endDate and target.beginDate > target.endDate:
        raise ValueError("enrollment beginDate must be on or before endDate")

    term_ids = _enrollment_list(class_row.termSourcedIds)
    if (target.beginDate or target.endDate) and term_ids:
        session_rows = connection.execute(
            select(sessions.c.startDate, sessions.c.endDate).where(sessions.c.sourcedId.in_(term_ids)),
        ).fetchall()
        if not any(
            (target.beginDate is None or (row.startDate <= target.beginDate <= row.endDate))
            and (target.endDate is None or (row.startDate <= target.endDate <= row.endDate))
            for row in session_rows
        ):
            raise ValueError("enrollment beginDate/endDate must fall within a class academic session period")

    if target.role != "teacher" or target.primary != "true":
        return

    enrollments = Enrollment.__table__
    statement = select(
        enrollments.c.sourcedId,
        enrollments.c.beginDate,
        enrollments.c.endDate,
    ).where(
        enrollments.c.classSourcedId == target.classSourcedId,
        enrollments.c.role == "teacher",
        enrollments.c.primary == "true",
    )

    if target.sourcedId:
        statement = statement.where(enrollments.c.sourcedId != target.sourcedId)

    for row in connection.execute(statement):
        if _enrollment_ranges_overlap(row.beginDate, row.endDate, target.beginDate, target.endDate):
            raise ValueError(
                "Only one primary teacher may be designated for a class during an overlapping period",
            )
