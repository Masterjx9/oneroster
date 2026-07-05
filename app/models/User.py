import json

from sqlalchemy import event, select
from sqlalchemy.orm import validates

from app import db
from app.models.Base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(255), nullable=False)
    userIds = db.Column(db.JSON, nullable=True, default=list)
    enabledUser = db.Column(
        db.Enum("true", "false", name="user_enabled", native_enum=False),
        nullable=False,
    )
    givenName = db.Column(db.String(255), nullable=False)
    familyName = db.Column(db.String(255), nullable=False)
    middleName = db.Column(db.String(255), nullable=True)
    role = db.Column(
        db.Enum(
            "administrator",
            "aide",
            "guardian",
            "parent",
            "proctor",
            "relative",
            "student",
            "teacher",
            name="user_role",
            native_enum=False,
        ),
        nullable=False,
    )
    identifier = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    sms = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    agents = db.Column(db.JSON, nullable=True, default=list)
    orgs = db.Column(db.JSON, nullable=False)
    grades = db.Column(db.JSON, nullable=True, default=list)
    password = db.Column(db.String(255), nullable=True)

    @validates("userIds")
    def validate_user_ids(self, key: str, values: list | None) -> list:
        user_ids = values or []
        if not isinstance(user_ids, list):
            raise ValueError("userIds must be a list")
        for value in user_ids:
            if not isinstance(value, dict):
                raise ValueError("Each userIds entry must be an object")
            if "type" not in value or "identifier" not in value:
                raise ValueError("Each userIds entry must include type and identifier")
            if not isinstance(value["type"], str) or not isinstance(value["identifier"], str):
                raise ValueError("userIds type and identifier must be strings")
        return user_ids

    @validates("agents")
    def validate_agents(self, key: str, values: list | None) -> list:
        agents = values or []
        if not isinstance(agents, list):
            raise ValueError("agents must be a list")
        for value in agents:
            if not isinstance(value, str):
                raise ValueError("agents must contain user sourcedIds")
        return agents

    @validates("orgs")
    def validate_orgs(self, key: str, values: list | None) -> list:
        orgs = values or []
        if not isinstance(orgs, list):
            raise ValueError("orgs must be a list")
        if not orgs:
            raise ValueError("orgs must contain at least one sourcedId")
        for value in orgs:
            if not isinstance(value, str):
                raise ValueError("orgs must contain org sourcedIds")
        return orgs

    @validates("grades")
    def validate_grades(self, key: str, values: list | None) -> list:
        grades = values or []
        if not isinstance(grades, list):
            raise ValueError("grades must be a list")
        for value in grades:
            if not isinstance(value, str):
                raise ValueError("grades must contain strings")
        return grades

    @property
    def user_ids(self) -> list[dict]:
        values = self.userIds or []
        return [
            {"type": value.get("type"), "identifier": value.get("identifier")}
            for value in values
            if isinstance(value, dict)
            and "type" in value
            and "identifier" in value
        ]

    @property
    def agent_refs(self) -> list[dict]:
        return [
            {
                "href": f"/users/{agent_id}",
                "sourcedId": agent_id,
                "type": "user",
            }
            for agent_id in (self.agents or [])
        ]

    @property
    def org_refs(self) -> list[dict]:
        return [
            {
                "href": f"/orgs/{org_id}",
                "sourcedId": org_id,
                "type": "org",
            }
            for org_id in (self.orgs or [])
        ]

    def to_dict(self) -> dict:
        payload = super().to_dict()

        payload["userIds"] = self.user_ids
        payload["agents"] = self.agent_refs
        payload["orgs"] = self.org_refs
        payload["grades"] = payload.get("grades") or []

        return payload


def _user_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


@event.listens_for(User, "before_insert")
@event.listens_for(User, "before_update")
def validate_agent_rules(mapper, connection, target: User) -> None:
    from app.models.Org import Org

    agent_ids = target.agents or []
    org_ids = target.orgs or []
    orgs = Org.__table__

    existing_orgs = {
        row.sourcedId
        for row in connection.execute(
            select(orgs.c.sourcedId).where(orgs.c.sourcedId.in_(org_ids)),
        )
    }
    if len(existing_orgs) != len(set(org_ids)):
        raise ValueError("All orgs must reference existing orgs")

    if target.role != "student" and (target.grades or []):
        raise ValueError("Only student users may have grades")

    relationship_roles = {"parent", "guardian", "relative", "aide"}

    if not agent_ids:
        if target.role in {"parent", "guardian", "relative"}:
            raise ValueError("Parent, guardian, and relative users must have student agents")
        return

    if target.role not in {"student", *relationship_roles}:
        raise ValueError("Only students, parents, guardians, relatives, and aides may use agents")

    users = User.__table__
    related_users = {
        row.sourcedId: row
        for row in connection.execute(
            select(users.c.sourcedId, users.c.role, users.c.agents).where(users.c.sourcedId.in_(agent_ids)),
        )
    }

    if len(related_users) != len(set(agent_ids)):
        raise ValueError("All agents must reference existing users")

    family_roles = {"parent", "guardian", "relative"}

    if target.role == "student":
        for agent_id in agent_ids:
            related_user = related_users[agent_id]
            if related_user.role not in relationship_roles:
                raise ValueError("Student agents may only be parents, guardians, relatives, or aides")
            if target.sourcedId not in _user_list(related_user.agents):
                raise ValueError("Student agent links must be reciprocal")

    if target.role in relationship_roles:
        for agent_id in agent_ids:
            related_user = related_users[agent_id]
            if related_user.role != "student":
                raise ValueError("Parent, guardian, relative, and aide users may only agent-link to students")
            if target.sourcedId not in _user_list(related_user.agents):
                raise ValueError("Parent, guardian, relative, and aide agent links must be reciprocal")
