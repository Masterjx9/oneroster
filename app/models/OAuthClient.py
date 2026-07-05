from app import db


ONEROSTER_SCOPES = [
    "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-core.readonly",
    "https://purl.imsglobal.org/spec/or/v1p1/scope/roster.readonly",
    "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-demographics.readonly",
    "https://purl.imsglobal.org/spec/or/v1p1/scope/resource.readonly",
    "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly",
    "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput",
    "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete",
]


class OAuthClient(db.Model):
    __tablename__ = "oauth_clients"

    client_id = db.Column(db.String(255), primary_key=True)
    client_secret = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False, default="OneRoster Client")
    is_confidential = db.Column(db.Boolean, nullable=False, default=True)
    scopes_text = db.Column("scopes", db.Text, nullable=False)

    @property
    def client_type(self) -> str:
        return "confidential" if self.is_confidential else "public"

    @property
    def redirect_uris(self) -> list[str]:
        return []

    @property
    def default_redirect_uri(self) -> None:
        return None

    @property
    def default_scopes(self) -> list[str]:
        return [scope for scope in self.scopes_text.split() if scope]

    @property
    def allowed_grant_types(self) -> list[str]:
        return ["client_credentials"]

    @property
    def allowed_response_types(self) -> list[str]:
        return []

    @property
    def user(self):
        return None

    def validate_scopes(self, scopes: list[str] | None) -> bool:
        requested_scopes = scopes or []
        if not requested_scopes:
            return False
        return set(requested_scopes).issubset(set(self.default_scopes))
