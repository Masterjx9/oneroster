from datetime import datetime, timedelta

from app import db


class OAuthToken(db.Model):
    __tablename__ = "oauth_tokens"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(255),
        db.ForeignKey("oauth_clients.client_id"),
        nullable=False,
        index=True,
    )
    access_token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    refresh_token = db.Column(db.String(255), nullable=True, unique=True, index=True)
    token_type = db.Column(db.String(32), nullable=False, default="bearer")
    scopes_text = db.Column("scopes", db.Text, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    client = db.relationship("OAuthClient", lazy="joined")

    @property
    def scopes(self) -> list[str]:
        return [scope for scope in self.scopes_text.split() if scope]

    @property
    def user(self):
        return None

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def from_token_payload(cls, token: dict, client_id: str) -> "OAuthToken":
        expires_in = int(token.get("expires_in", 3600))
        return cls(
            client_id=client_id,
            access_token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_type=str(token.get("token_type", "bearer")).lower(),
            scopes_text=token.get("scope", ""),
            expires=datetime.utcnow() + timedelta(seconds=expires_in),
        )
