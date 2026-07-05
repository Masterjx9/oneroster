from sqlalchemy import event, select

from app import db
from app.models.Base import BaseModel


class Org(BaseModel):
    __tablename__ = "orgs"

    name = db.Column(db.String(255), nullable=False)
    type = db.Column(
        db.Enum(
            "department",
            "school",
            "district",
            "local",
            "state",
            "national",
            name="org_type",
            native_enum=False,
        ),
        nullable=False,
    )
    identifier = db.Column(db.String(255), nullable=True)
    parentSourcedId = db.Column(
        db.String(255),
        db.ForeignKey("orgs.sourcedId"),
        nullable=True,
    )
    parent_record = db.relationship(
        "Org",
        remote_side="Org.sourcedId",
        backref=db.backref("children_records", lazy="select"),
    )

    @property
    def parent(self) -> dict | None:
        if not self.parentSourcedId:
            return None
        return {
            "href": f"/orgs/{self.parentSourcedId}",
            "sourcedId": self.parentSourcedId,
            "type": "org",
        }

    @property
    def children(self) -> list[dict]:
        return [
            {
                "href": f"/orgs/{child.sourcedId}",
                "sourcedId": child.sourcedId,
                "type": "org",
            }
            for child in self.children_records
        ]

    def to_dict(self) -> dict:
        payload = super().to_dict()

        payload["parent"] = self.parent
        payload["children"] = self.children
        payload.pop("parentSourcedId", None)

        return payload


_ALLOWED_PARENT_TYPES_BY_ORG_TYPE = {
    "state": {"national"},
    "local": {"state", "department"},
    "district": {"local", "department"},
    "school": {"district", "department"},
    "department": {"state", "local", "district", "school", "department"},
}


@event.listens_for(Org, "before_insert")
@event.listens_for(Org, "before_update")
def validate_org_hierarchy(mapper, connection, target: Org) -> None:
    if not target.parentSourcedId:
        return

    if target.parentSourcedId == target.sourcedId:
        raise ValueError("org parent cannot reference itself")

    orgs = Org.__table__
    parent_type = connection.execute(
        select(orgs.c.type).where(orgs.c.sourcedId == target.parentSourcedId),
    ).scalar_one_or_none()

    if parent_type is None:
        raise ValueError("org parent must reference an existing org")

    if target.type == "national":
        raise ValueError("national orgs cannot have a parent")

    allowed_parent_types = _ALLOWED_PARENT_TYPES_BY_ORG_TYPE.get(target.type)
    if allowed_parent_types and parent_type not in allowed_parent_types:
        raise ValueError(f"{target.type} orgs cannot have a parent of type {parent_type}")
