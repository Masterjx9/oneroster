import json

from sqlalchemy import event, select
from sqlalchemy.orm import validates

from app import db
from app.models.Base import BaseModel


class Resource(BaseModel):
    __tablename__ = "resources"

    title = db.Column(db.String(255), nullable=True)
    roles = db.Column(db.JSON, nullable=True, default=list)
    importance = db.Column(
        db.Enum("primary", "secondary", name="importance_type", native_enum=False),
        nullable=True,
    )
    vendorResourceId = db.Column(db.String(255), nullable=False)
    vendorId = db.Column(db.String(255), nullable=True)
    applicationId = db.Column(db.String(255), nullable=True)

    @validates("roles")
    def validate_roles(self, key: str, roles: list | None) -> list:
        allowed = {
            "administrator",
            "aide",
            "guardian",
            "parent",
            "proctor",
            "relative",
            "student",
            "teacher",
        }
        values = roles or []
        if not isinstance(values, list):
            raise ValueError("roles must be a list")
        if any(role not in allowed for role in values):
            raise ValueError("Invalid resource role")
        return values

    def to_dict(self) -> dict:
        payload = super().to_dict()
        payload["roles"] = payload.get("roles") or []
        return payload


def _resource_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


@event.listens_for(Resource, "before_insert")
@event.listens_for(Resource, "before_update")
def validate_resource_association(mapper, connection, target: Resource) -> None:
    if not target.sourcedId:
        return

    from app.models.Class import Class
    from app.models.Course import Course

    classes = Class.__table__
    courses = Course.__table__

    course_links = connection.execute(select(courses.c.resourceSourcedIds)).fetchall()
    class_links = connection.execute(select(classes.c.resourceSourcedIds)).fetchall()

    linked = any(
        target.sourcedId in _resource_list(row.resourceSourcedIds)
        for row in course_links + class_links
    )

    if not linked:
        raise ValueError("Resource must be associated to at least one course or class")
