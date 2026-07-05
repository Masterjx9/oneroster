from datetime import date

from sqlalchemy import event, select

from app import db
from app.models.Base import BaseModel


class AcademicSession(BaseModel):
    __tablename__ = "academic_sessions"

    title = db.Column(db.String(255), nullable=False)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    type = db.Column(
        db.Enum(
            "gradingPeriod",
            "semester",
            "schoolYear",
            "term",
            name="academic_session_type",
            native_enum=False,
        ),
        nullable=False,
    )
    parentSourcedId = db.Column(
        db.String(255),
        db.ForeignKey("academic_sessions.sourcedId"),
        nullable=True,
    )
    schoolYear = db.Column(db.String(4), nullable=False)
    parent_record = db.relationship(
        "AcademicSession",
        remote_side="AcademicSession.sourcedId",
        backref=db.backref("children_records", lazy="select"),
    )

    @property
    def parent(self) -> dict | None:
        if not self.parentSourcedId:
            return None
        return {
            "href": f"/academicSessions/{self.parentSourcedId}",
            "sourcedId": self.parentSourcedId,
            "type": "academicSession",
        }

    @property
    def children(self) -> list[dict]:
        return [
            {
                "href": f"/academicSessions/{child.sourcedId}",
                "sourcedId": child.sourcedId,
                "type": "academicSession",
            }
            for child in self.children_records
        ]

    def to_dict(self) -> dict:
        payload = super().to_dict()

        if isinstance(payload.get("startDate"), date):
            payload["startDate"] = payload["startDate"].isoformat()

        if isinstance(payload.get("endDate"), date):
            payload["endDate"] = payload["endDate"].isoformat()

        payload["parent"] = self.parent
        payload["children"] = self.children
        payload.pop("parentSourcedId", None)

        return payload


@event.listens_for(AcademicSession, "before_insert")
@event.listens_for(AcademicSession, "before_update")
def validate_academic_session_rules(mapper, connection, target: AcademicSession) -> None:
    sessions = AcademicSession.__table__

    if target.startDate > target.endDate:
        raise ValueError("academicSession startDate must be on or before endDate")

    if len(target.schoolYear) != 4 or not target.schoolYear.isdigit():
        raise ValueError("schoolYear must be a 4-digit gYear")

    if target.parentSourcedId == target.sourcedId:
        raise ValueError("academicSession parent cannot reference itself")

    if target.type == "schoolYear" and target.parentSourcedId:
        raise ValueError("schoolYear academic sessions cannot have a parent")

    if not target.parentSourcedId:
        if target.type == "gradingPeriod":
            raise ValueError("gradingPeriod academic sessions must have a parent term")
        if target.type == "schoolYear" or target.startDate.year != target.endDate.year:
            if target.schoolYear != str(target.endDate.year):
                raise ValueError("academicSession schoolYear must include the school year end")
        return

    parent_type = connection.execute(
        select(sessions.c.type).where(sessions.c.sourcedId == target.parentSourcedId),
    ).scalar_one_or_none()

    if parent_type is None:
        raise ValueError("academicSession parent must reference an existing academic session")

    parent_school_year = connection.execute(
        select(sessions.c.schoolYear).where(sessions.c.sourcedId == target.parentSourcedId),
    ).scalar_one()

    if target.schoolYear != parent_school_year:
        raise ValueError("academicSession schoolYear must match the parent academic session schoolYear")

    if target.type in {"term", "semester"} and parent_type != "schoolYear":
        raise ValueError("term and semester academic sessions must have a schoolYear parent")

    if target.type == "gradingPeriod" and parent_type != "term":
        raise ValueError("gradingPeriod parent must be a term academic session")
