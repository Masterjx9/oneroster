import json

from sqlalchemy import event, select
from sqlalchemy.orm import validates

from app import db
from app.models.Base import BaseModel


class Course(BaseModel):
    __tablename__ = "courses"

    title = db.Column(db.String(255), nullable=False)
    schoolYearSourcedId = db.Column(db.String(255), nullable=True)
    courseCode = db.Column(db.String(255), nullable=True)
    grades = db.Column(db.JSON, nullable=True, default=list)
    subjects = db.Column(db.JSON, nullable=True, default=list)
    orgSourcedId = db.Column(db.String(255), nullable=False)
    subjectCodes = db.Column(db.JSON, nullable=True, default=list)
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

    @validates("grades", "subjects", "subjectCodes", "resourceSourcedIds")
    def validate_string_lists(self, key: str, values: list | None) -> list:
        return self._validate_string_list(values, key)

    @property
    def schoolYear(self) -> dict | None:
        if not self.schoolYearSourcedId:
            return None
        return {
            "href": f"/academicSessions/{self.schoolYearSourcedId}",
            "sourcedId": self.schoolYearSourcedId,
            "type": "academicSession",
        }

    @property
    def org(self) -> dict:
        return {
            "href": f"/orgs/{self.orgSourcedId}",
            "sourcedId": self.orgSourcedId,
            "type": "org",
        }

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

        payload.pop("schoolYearSourcedId", None)
        payload.pop("orgSourcedId", None)
        payload.pop("resourceSourcedIds", None)

        payload["schoolYear"] = self.schoolYear
        payload["org"] = self.org
        payload["resources"] = self.resources

        return payload


def _course_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


@event.listens_for(Course, "before_insert")
@event.listens_for(Course, "before_update")
def validate_course_rules(mapper, connection, target: Course) -> None:
    from app.models.AcademicSessions import AcademicSession
    from app.models.Org import Org
    from app.models.Resource import Resource

    orgs = Org.__table__
    sessions = AcademicSession.__table__
    resources = Resource.__table__

    if connection.execute(
        select(orgs.c.sourcedId).where(orgs.c.sourcedId == target.orgSourcedId),
    ).scalar_one_or_none() is None:
        raise ValueError("course org must reference an existing org")

    if target.schoolYearSourcedId:
        school_year_type = connection.execute(
            select(sessions.c.type).where(sessions.c.sourcedId == target.schoolYearSourcedId),
        ).scalar_one_or_none()
        if school_year_type != "schoolYear":
            raise ValueError("course schoolYear must reference a schoolYear academic session")

    resource_ids = target.resourceSourcedIds or []
    if resource_ids:
        resource_rows = connection.execute(
            select(resources.c.sourcedId).where(resources.c.sourcedId.in_(resource_ids)),
        ).fetchall()
        if len(resource_rows) != len(set(resource_ids)):
            raise ValueError("course resources must reference existing resources")

    if target.sourcedId:
        current = connection.execute(
            select(Course.__table__.c.resourceSourcedIds).where(Course.__table__.c.sourcedId == target.sourcedId),
        ).scalar_one_or_none()
        removed = set(_course_list(current)) - set(resource_ids)
        from app.models.Class import Class
        for removed_id in removed:
            still_linked_in_courses = any(
                removed_id in _course_list(row.resourceSourcedIds)
                for row in connection.execute(
                    select(Course.__table__.c.resourceSourcedIds).where(Course.__table__.c.sourcedId != target.sourcedId),
                )
            )
            still_linked_in_classes = any(
                removed_id in _course_list(row.resourceSourcedIds)
                for row in connection.execute(select(Class.__table__.c.resourceSourcedIds))
            )
            if not still_linked_in_courses and not still_linked_in_classes:
                raise ValueError("resource must remain associated to at least one class or course")
