from app import db
from app.models.Base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    title = db.Column(db.String(255), nullable=False)
