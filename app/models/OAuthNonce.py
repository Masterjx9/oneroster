from datetime import UTC, datetime

from app import db


class OAuthNonce(db.Model):
    __tablename__ = "oauth_nonces"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(
        db.String(255),
        db.ForeignKey("oauth_clients.client_id"),
        nullable=False,
        index=True,
    )
    nonce = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(32), nullable=False)
    token_key = db.Column(db.String(255), nullable=False, default="")
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "client_id",
            "timestamp",
            "nonce",
            "token_key",
            name="uq_oauth_nonce_request",
        ),
    )
