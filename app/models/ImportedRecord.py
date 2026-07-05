from datetime import datetime

from app import db


class ImportedRecord(db.Model):
    __tablename__ = "imported_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_configuration_id = db.Column(
        db.Integer,
        db.ForeignKey("provider_configurations.id"),
        nullable=False,
        index=True,
    )
    import_run_id = db.Column(
        db.Integer,
        db.ForeignKey("provider_import_runs.id"),
        nullable=False,
        index=True,
    )
    resource_type = db.Column(db.String(64), nullable=False, index=True)
    sourced_id = db.Column(db.String(255), nullable=False)
    payload_json = db.Column("payload", db.JSON, nullable=False)
    imported_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    import_run = db.relationship("ProviderImportRun", back_populates="imported_records")

    __table_args__ = (
        db.UniqueConstraint(
            "import_run_id",
            "resource_type",
            "sourced_id",
            name="uq_imported_record_per_run",
        ),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "providerConfigurationId": self.provider_configuration_id,
            "importRunId": self.import_run_id,
            "resourceType": self.resource_type,
            "sourcedId": self.sourced_id,
            "payload": self.payload_json,
            "importedAt": self.imported_at.isoformat() if self.imported_at else None,
        }
