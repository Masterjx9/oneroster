import json
import os
from datetime import UTC, datetime
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_oauthlib.utils import create_response
from oauthlib.oauth1 import RequestValidator, SignatureOnlyEndpoint

from app import db, oauth
from app.models.OAuthClient import OAuthClient
from app.models.OAuthNonce import OAuthNonce
from app.models.OAuthToken import OAuthToken


oauth_routes = Blueprint("oauth_routes", __name__)

ROSTER_CORE_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-core.readonly"
ROSTER_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/roster.readonly"
ROSTER_DEMOGRAPHICS_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-demographics.readonly"
RESOURCE_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/resource.readonly"
GRADEBOOK_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
GRADEBOOK_CREATEPUT_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput"
GRADEBOOK_DELETE_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete"


class OneRosterOAuth1RequestValidator(RequestValidator):
    @property
    def allowed_signature_methods(self):
        return ("HMAC-SHA1",)

    @property
    def safe_characters(self):
        return set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~")

    @property
    def client_key_length(self):
        return 1, 255

    @property
    def nonce_length(self):
        return 1, 255

    @property
    def enforce_ssl(self):
        return os.environ.get("OAUTHLIB_INSECURE_TRANSPORT") not in {"1", "true", "True"}

    @property
    def dummy_client(self):
        return "dummy-oneroster-client"

    @property
    def dummy_request_token(self):
        return "dummy-request-token"

    @property
    def dummy_access_token(self):
        return "dummy-access-token"

    def get_client_secret(self, client_key, request):
        client = OAuthClient.query.filter_by(client_id=client_key).first()
        return client.client_secret if client else "dummy-oneroster-secret"

    def get_request_token_secret(self, client_key, token, request):
        return ""

    def get_access_token_secret(self, client_key, token, request):
        return ""

    def get_default_realms(self, client_key, request):
        client = OAuthClient.query.filter_by(client_id=client_key).first()
        return client.default_scopes if client else []

    def get_realms(self, token, request):
        return []

    def get_redirect_uri(self, token, request):
        return None

    def get_rsa_key(self, client_key, request):
        return None

    def invalidate_request_token(self, client_key, request_token, request):
        return None

    def validate_client_key(self, client_key, request):
        return OAuthClient.query.filter_by(client_id=client_key).first() is not None

    def validate_request_token(self, client_key, token, request):
        return False

    def validate_access_token(self, client_key, token, request):
        return False

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        try:
            request_timestamp = int(timestamp)
        except (TypeError, ValueError):
            return False

        current_timestamp = int(datetime.now(UTC).timestamp())
        if abs(current_timestamp - request_timestamp) > self.timestamp_lifetime:
            return False

        token_key = access_token or request_token or getattr(request, "resource_owner_key", None) or ""
        existing_nonce = OAuthNonce.query.filter_by(
            client_id=client_key,
            timestamp=str(timestamp),
            nonce=nonce,
            token_key=token_key,
        ).first()
        if existing_nonce:
            return False

        db.session.add(
            OAuthNonce(
                client_id=client_key,
                timestamp=str(timestamp),
                nonce=nonce,
                token_key=token_key,
            )
        )
        db.session.commit()
        return True

    def validate_redirect_uri(self, client_key, redirect_uri, request):
        return False

    def validate_requested_realms(self, client_key, realms, request):
        client = OAuthClient.query.filter_by(client_id=client_key).first()
        if client is None:
            return False
        return set(realms or []).issubset(set(client.default_scopes))

    def validate_realms(self, client_key, token, request, uri=None, realms=None):
        client = OAuthClient.query.filter_by(client_id=client_key).first()
        if client is None:
            return False
        return set(realms or []).issubset(set(client.default_scopes))

    def validate_verifier(self, client_key, token, verifier, request):
        return False

    def verify_request_token(self, token, request):
        return False

    def verify_realms(self, token, realms, request):
        return False

    def save_access_token(self, token, request):
        return None

    def save_request_token(self, token, request):
        return None

    def save_verifier(self, token, verifier, request):
        return None


_oauth1_signature_endpoint = SignatureOnlyEndpoint(OneRosterOAuth1RequestValidator())


def _extract_token_request_params() -> tuple[str, str, dict, dict]:
    uri = request.base_url
    if request.query_string:
        uri += f"?{request.query_string.decode('utf-8')}"

    headers = dict(request.headers)
    if request.authorization:
        headers["Authorization"] = {
            "username": request.authorization.username,
            "password": request.authorization.password,
        }

    return uri, request.method, request.form.to_dict(), headers


def _extract_signed_request_params() -> tuple[str, str, str, dict]:
    uri = request.base_url
    if request.query_string:
        uri += f"?{request.query_string.decode('utf-8')}"

    return (
        uri,
        request.method,
        request.get_data(as_text=True),
        dict(request.headers),
    )


@oauth.clientgetter
def get_oauth_client(client_id: str) -> OAuthClient | None:
    return OAuthClient.query.filter_by(client_id=client_id).first()


@oauth.tokengetter
def get_oauth_token(access_token: str | None = None, refresh_token: str | None = None) -> OAuthToken | None:
    if access_token:
        return OAuthToken.query.filter_by(access_token=access_token).first()
    if refresh_token:
        return OAuthToken.query.filter_by(refresh_token=refresh_token).first()
    return None


@oauth.tokensetter
def save_oauth_token(token: dict, request, *args, **kwargs) -> None:
    oauth_token = OAuthToken.from_token_payload(token, request.client.client_id)
    db.session.add(oauth_token)
    db.session.commit()


@oauth.grantgetter
def get_oauth_grant(client_id, code):
    return None


@oauth.grantsetter
def save_oauth_grant(client_id, code, request, *args, **kwargs) -> None:
    return None


def _authorize_bearer_request(scopes: tuple[str, ...]):
    auth_header = request.headers.get("Authorization", "")
    access_token = auth_header.split(" ", 1)[1].strip()
    token = get_oauth_token(access_token=access_token)
    if token is None:
        return jsonify(error="invalid_token"), 401

    if token.expires and datetime.utcnow() > token.expires:
        return jsonify(error="invalid_token"), 401

    if scopes and not set(scopes).issubset(set(token.scopes)):
        return jsonify(error="insufficient_scope"), 403

    request.oauth_token = token
    request.oauth_client = token.client
    return None


def _authorize_oauth1_request(scopes: tuple[str, ...]):
    uri, http_method, body, headers = _extract_signed_request_params()
    is_valid, oauth_request = _oauth1_signature_endpoint.validate_request(
        uri,
        http_method=http_method,
        body=body,
        headers=headers,
    )
    if not is_valid or oauth_request is None or not oauth_request.client_key:
        return jsonify(error="invalid_signature"), 401

    client = get_oauth_client(oauth_request.client_key)
    if client is None:
        return jsonify(error="invalid_client"), 401

    if scopes and not set(scopes).issubset(set(client.default_scopes)):
        return jsonify(error="insufficient_scope"), 403

    request.oauth_client = client
    request.oauth_signature = oauth_request
    return None


def bearer_token_required(*scopes: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                authorization_error = _authorize_bearer_request(scopes)
            elif auth_header.startswith("OAuth "):
                authorization_error = _authorize_oauth1_request(scopes)
            else:
                return jsonify(error="invalid_token"), 401

            if authorization_error is not None:
                return authorization_error

            return f(*args, **kwargs)

        return decorated

    return decorator


@oauth_routes.route("/token", methods=["POST"])
def issue_token():
    if not request.form.get("scope", "").strip():
        return (
            jsonify(
                error="invalid_request",
                error_description="scope is required",
            ),
            400,
        )

    uri, http_method, body, headers = _extract_token_request_params()
    response_headers, response_body, status = oauth.server.create_token_response(
        uri,
        http_method,
        body,
        headers,
        {},
    )

    if response_body:
        payload = json.loads(response_body)
        if isinstance(payload, dict) and "token_type" in payload:
            payload["token_type"] = "bearer"
            response_body = json.dumps(payload)

    return create_response(response_headers, response_body, status)
