from sqlalchemy import event, select

from app import db
from app.models.Base import BaseModel


class LineItem(BaseModel):
    __tablename__ = "line_items"

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    assignDate = db.Column(db.DateTime(timezone=True), nullable=False)
    dueDate = db.Column(db.DateTime(timezone=True), nullable=False)
    classSourcedId = db.Column(db.String(255), nullable=False)
    categorySourcedId = db.Column(db.String(255), nullable=False)
    gradingPeriodSourcedId = db.Column(db.String(255), nullable=False)
    resultValueMin = db.Column(db.Float, nullable=False)
    resultValueMax = db.Column(db.Float, nullable=False)

    @property
    def category(self) -> dict:
        return {
            "href": f"/categories/{self.categorySourcedId}",
            "sourcedId": self.categorySourcedId,
            "type": "category",
        }

    @property
    def gradingPeriod(self) -> dict:
        return {
            "href": f"/academicSessions/{self.gradingPeriodSourcedId}",
            "sourcedId": self.gradingPeriodSourcedId,
            "type": "academicSession",
        }

    def to_dict(self) -> dict:
        payload = super().to_dict()

        payload.pop("classSourcedId", None)
        payload.pop("categorySourcedId", None)
        payload.pop("gradingPeriodSourcedId", None)

        payload["class"] = getattr(self, "class")
        payload["category"] = self.category
        payload["gradingPeriod"] = self.gradingPeriod

        return payload

    def class_guid_ref(self) -> dict:
        return {
            "href": f"/classes/{self.classSourcedId}",
            "sourcedId": self.classSourcedId,
            "type": "class",
        }

    locals()["class"] = property(class_guid_ref)


@event.listens_for(LineItem, "before_insert")
@event.listens_for(LineItem, "before_update")
def validate_line_item_rules(mapper, connection, target: LineItem) -> None:
    from app.models.AcademicSessions import AcademicSession
    from app.models.Category import Category
    from app.models.Class import Class

    classes = Class.__table__
    categories = Category.__table__
    sessions = AcademicSession.__table__

    if connection.execute(
        select(classes.c.sourcedId).where(classes.c.sourcedId == target.classSourcedId),
    ).scalar_one_or_none() is None:
        raise ValueError("lineItem class must reference an existing class")

    if connection.execute(
        select(categories.c.sourcedId).where(categories.c.sourcedId == target.categorySourcedId),
    ).scalar_one_or_none() is None:
        raise ValueError("lineItem category must reference an existing category")

    grading_type = connection.execute(
        select(sessions.c.type).where(sessions.c.sourcedId == target.gradingPeriodSourcedId),
    ).scalar_one_or_none()
    if grading_type != "gradingPeriod":
        raise ValueError("lineItem gradingPeriod must reference a gradingPeriod academic session")

    if target.assignDate > target.dueDate:
        raise ValueError("lineItem assignDate must be on or before dueDate")

    if target.resultValueMax < target.resultValueMin:
        raise ValueError("lineItem resultValueMax must be greater than or equal to resultValueMin")
