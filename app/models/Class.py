import json

from sqlalchemy import event, select
from sqlalchemy.orm import validates

from app import db
from app.models.Base import BaseModel


class Class(BaseModel):
    __tablename__ = "classes"

    title = db.Column(db.String(255), nullable=False)
    classCode = db.Column(db.String(255), nullable=True)
    classType = db.Column(
        db.Enum(
            "homeroom",
            "scheduled",
            name="class_type",
            native_enum=False,
        ),
        nullable=False,
    )
    location = db.Column(db.String(255), nullable=True)
    grades = db.Column(db.JSON, nullable=True, default=list)
    subjects = db.Column(db.JSON, nullable=True, default=list)
    courseSourcedId = db.Column(db.String(255), nullable=False)
    schoolSourcedId = db.Column(db.String(255), nullable=False)
    termSourcedIds = db.Column(db.JSON, nullable=False)
    subjectCodes = db.Column(db.JSON, nullable=True, default=list)
    periods = db.Column(db.JSON, nullable=True, default=list)
    resourceSourcedIds = db.Column(db.JSON, nullable=True, default=list)

    @staticmethod
    def _validate_string_list(values: list | None, field_name: str) -> list:
        items = values or []
        if not isinstance(items, list):
            raise ValueError(f"{field_name} must be a list")
        for value in items:
            if not isinstance(value, str):
                raise ValueError(f"{field_name} must contain strings")
        return items

    @validates("termSourcedIds")
    def validate_terms(self, key: str, values: list | None) -> list:
        terms = self._validate_string_list(values, "termSourcedIds")
        if not terms:
            raise ValueError("termSourcedIds must contain at least one academic session sourcedId")
        return terms

    @validates("grades", "subjects", "subjectCodes", "periods", "resourceSourcedIds")
    def validate_string_lists(self, key: str, values: list | None) -> list:
        return self._validate_string_list(values, key)

    @property
    def course(self) -> dict:
        return {
            "href": f"/courses/{self.courseSourcedId}",
            "sourcedId": self.courseSourcedId,
            "type": "course",
        }

    @property
    def school(self) -> dict:
        return {
            "href": f"/schools/{self.schoolSourcedId}",
            "sourcedId": self.schoolSourcedId,
            "type": "org",
        }

    @property
    def terms(self) -> list[dict]:
        return [
            {
                "href": f"/academicSessions/{term_id}",
                "sourcedId": term_id,
                "type": "academicSession",
            }
            for term_id in (self.termSourcedIds or [])
        ]

    @property
    def resources(self) -> list[dict]:
        return [
            {
                "href": f"/resources/{resource_id}",
                "sourcedId": resource_id,
                "type": "resource",
            }
            for resource_id in (self.resourceSourcedIds or [])
        ]

    def to_dict(self) -> dict:
        payload = super().to_dict()

        payload["grades"] = payload.get("grades") or []
        payload["subjects"] = payload.get("subjects") or []
        payload["subjectCodes"] = payload.get("subjectCodes") or []
        payload["periods"] = payload.get("periods") or []

        payload.pop("courseSourcedId", None)
        payload.pop("schoolSourcedId", None)
        payload.pop("termSourcedIds", None)
        payload.pop("resourceSourcedIds", None)

        payload["course"] = self.course
        payload["school"] = self.school
        payload["terms"] = self.terms
        payload["resources"] = self.resources

        return payload


def _class_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


@event.listens_for(Class, "before_insert")
@event.listens_for(Class, "before_update")
def validate_class_rules(mapper, connection, target: Class) -> None:
    from app.models.AcademicSessions import AcademicSession
    from app.models.Course import Course
    from app.models.Org import Org
    from app.models.Resource import Resource

    courses = Course.__table__
    orgs = Org.__table__
    sessions = AcademicSession.__table__
    resources = Resource.__table__

    if connection.execute(
        select(courses.c.sourcedId).where(courses.c.sourcedId == target.courseSourcedId),
    ).scalar_one_or_none() is None:
        raise ValueError("class course must reference an existing course")

    school_type = connection.execute(
        select(orgs.c.type).where(orgs.c.sourcedId == target.schoolSourcedId),
    ).scalar_one_or_none()
    if school_type != "school":
        raise ValueError("class school must reference an org of type school")

    terms = target.termSourcedIds or []
    session_rows = connection.execute(
        select(sessions.c.sourcedId, sessions.c.type).where(sessions.c.sourcedId.in_(terms)),
    ).fetchall()
    if len(session_rows) != len(set(terms)):
        raise ValueError("class terms must reference existing academic sessions")
    if any(row.type not in {"term", "semester"} for row in session_rows):
        raise ValueError("class terms must reference term or semester academic sessions")

    resource_ids = target.resourceSourcedIds or []
    if resource_ids:
        resource_rows = connection.execute(
            select(resources.c.sourcedId).where(resources.c.sourcedId.in_(resource_ids)),
        ).fetchall()
        if len(resource_rows) != len(set(resource_ids)):
            raise ValueError("class resources must reference existing resources")

    if target.sourcedId:
        current = connection.execute(
            select(Class.__table__.c.resourceSourcedIds).where(Class.__table__.c.sourcedId == target.sourcedId),
        ).scalar_one_or_none()
        removed = set(_class_list(current)) - set(resource_ids)
        for removed_id in removed:
            still_linked_in_classes = any(
                removed_id in _class_list(row.resourceSourcedIds)
                for row in connection.execute(
                    select(Class.__table__.c.resourceSourcedIds).where(Class.__table__.c.sourcedId != target.sourcedId),
                )
            )
            still_linked_in_courses = any(
                removed_id in _class_list(row.resourceSourcedIds)
                for row in connection.execute(select(courses.c.resourceSourcedIds))
            )
            if not still_linked_in_classes and not still_linked_in_courses:
                raise ValueError("resource must remain associated to at least one class or course")
