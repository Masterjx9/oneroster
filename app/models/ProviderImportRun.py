from datetime import datetime

from app import db


class ProviderImportRun(db.Model):
    __tablename__ = "provider_import_runs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_configuration_id = db.Column(
        db.Integer,
        db.ForeignKey("provider_configurations.id"),
        nullable=False,
        index=True,
    )
    status = db.Column(db.String(32), nullable=False, default="pending")
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    counts_json = db.Column("counts", db.JSON, nullable=True)

    provider_configuration = db.relationship("ProviderConfiguration", back_populates="import_runs")
    imported_records = db.relationship(
        "ImportedRecord",
        back_populates="import_run",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "providerConfigurationId": self.provider_configuration_id,
            "status": self.status,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "finishedAt": self.finished_at.isoformat() if self.finished_at else None,
            "errorMessage": self.error_message,
            "counts": self.counts_json or {},
        }
