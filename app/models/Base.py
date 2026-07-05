from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import event
from sqlalchemy.orm import validates

from app import db


def _normalize_status_value(value: str | None) -> str:
    if not value:
        return "active"
    if value == "inactive":
        return "tobedeleted"
    if value not in {"active", "tobedeleted"}:
        raise ValueError("status must be active, tobedeleted, or legacy inactive")
    return value


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sourcedId = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    status = db.Column(db.String(32), nullable=False, default="active")
    dateLastModified = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    metadata_json = db.Column("metadata", db.JSON, nullable=True)

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('active', 'tobedeleted')",
            name="ck_status_allowed_values",
        ),
    )

    @validates("metadata_json")
    def validate_metadata(self, key: str, value: dict | None) -> dict | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("metadata must be a name/value object")
        for metadata_key in value.keys():
            if not isinstance(metadata_key, str):
                raise ValueError("metadata keys must be strings")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str | None) -> str:
        return _normalize_status_value(value)

    @classmethod
    def get_by_sourced_id(cls, sourced_id: str):
        return cls.query.filter_by(sourcedId=sourced_id).first()

    def to_dict(self) -> dict:
        payload = {}

        for column in self.__table__.columns:
            key = column.name
            if key == "id":
                continue
            attribute_name = "metadata_json" if key == "metadata" else key
            value = getattr(self, attribute_name)

            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=UTC)
                else:
                    value = value.astimezone(UTC)
                value = value.isoformat(timespec="milliseconds").replace("+00:00", "Z")

            payload[key] = value

        return payload


@event.listens_for(BaseModel, "before_insert", propagate=True)
@event.listens_for(BaseModel, "before_update", propagate=True)
def ensure_base_defaults(mapper, connection, target: BaseModel) -> None:
    if not target.sourcedId:
        target.sourcedId = str(uuid4())
    target.status = _normalize_status_value(target.status)
    if target.dateLastModified is None:
        target.dateLastModified = datetime.now(UTC)
    elif target.dateLastModified.tzinfo is None:
        target.dateLastModified = target.dateLastModified.replace(tzinfo=UTC)
    else:
        target.dateLastModified = target.dateLastModified.astimezone(UTC)
