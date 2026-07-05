from datetime import date

from sqlalchemy import event, select

from app import db
from app.models.Base import BaseModel


class Result(BaseModel):
    __tablename__ = "results"

    lineItemSourcedId = db.Column(db.String(255), nullable=False)
    studentSourcedId = db.Column(db.String(255), nullable=False)
    scoreStatus = db.Column(
        db.Enum(
            "exempt",
            "fully graded",
            "not submitted",
            "partially graded",
            "submitted",
            name="result_score_status",
            native_enum=False,
        ),
        nullable=False,
    )
    score = db.Column(db.Float, nullable=False)
    scoreDate = db.Column(db.Date, nullable=False)
    comment = db.Column(db.String(255), nullable=True)

    @property
    def lineItem(self) -> dict:
        return {
            "href": f"/lineItems/{self.lineItemSourcedId}",
            "sourcedId": self.lineItemSourcedId,
            "type": "lineItem",
        }

    @property
    def student(self) -> dict:
        return {
            "href": f"/students/{self.studentSourcedId}",
            "sourcedId": self.studentSourcedId,
            "type": "student",
        }

    def to_dict(self) -> dict:
        payload = super().to_dict()

        payload.pop("lineItemSourcedId", None)
        payload.pop("studentSourcedId", None)

        if isinstance(payload.get("scoreDate"), date):
            payload["scoreDate"] = payload["scoreDate"].isoformat()

        payload["lineItem"] = self.lineItem
        payload["student"] = self.student

        return payload


@event.listens_for(Result, "before_insert")
@event.listens_for(Result, "before_update")
def validate_result_rules(mapper, connection, target: Result) -> None:
    from app.models.Enrollment import Enrollment
    from app.models.LineItem import LineItem
    from app.models.User import User

    enrollments = Enrollment.__table__
    line_items = LineItem.__table__
    users = User.__table__

    line_item = connection.execute(
        select(line_items.c.classSourcedId, line_items.c.resultValueMin, line_items.c.resultValueMax).where(
            line_items.c.sourcedId == target.lineItemSourcedId,
        ),
    ).first()
    if line_item is None:
        raise ValueError("result lineItem must reference an existing line item")

    student_role = connection.execute(
        select(users.c.role).where(users.c.sourcedId == target.studentSourcedId),
    ).scalar_one_or_none()
    if student_role != "student":
        raise ValueError("result student must reference an existing student user")

    if connection.execute(
        select(enrollments.c.sourcedId).where(
            enrollments.c.userSourcedId == target.studentSourcedId,
            enrollments.c.classSourcedId == line_item.classSourcedId,
            enrollments.c.role == "student",
        ),
    ).scalar_one_or_none() is None:
        raise ValueError("result student must be enrolled in the linked line item class")

    if not (line_item.resultValueMin <= target.score <= line_item.resultValueMax):
        raise ValueError("result score must be within the linked line item range")
