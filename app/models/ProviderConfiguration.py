from datetime import datetime

from app import db


DEFAULT_PROVIDER_SCOPES = " ".join(
    [
        "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-core.readonly",
        "https://purl.imsglobal.org/spec/or/v1p1/scope/roster.readonly",
        "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-demographics.readonly",
    ]
)


class ProviderConfiguration(db.Model):
    __tablename__ = "provider_configurations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    base_url = db.Column(db.String(2048), nullable=False)
    token_url = db.Column(db.String(2048), nullable=True)
    client_id = db.Column(db.String(255), nullable=False)
    client_secret = db.Column(db.String(255), nullable=False)
    scopes_text = db.Column("scopes", db.Text, nullable=False, default=DEFAULT_PROVIDER_SCOPES)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    import_runs = db.relationship(
        "ProviderImportRun",
        back_populates="provider_configuration",
        cascade="all, delete-orphan",
        lazy="select",
    )

    @property
    def scopes(self) -> list[str]:
        return [scope for scope in self.scopes_text.split() if scope]

    @property
    def resolved_token_url(self) -> str:
        if self.token_url:
            return self.token_url.rstrip("/")
        return f"{self.base_url.rstrip('/')}/token"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "baseUrl": self.base_url,
            "tokenUrl": self.resolved_token_url,
            "clientId": self.client_id,
            "clientSecretConfigured": bool(self.client_secret),
            "scopes": self.scopes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
