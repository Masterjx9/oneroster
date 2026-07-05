from flask import Blueprint, request

from app import db
from app.models.ProviderConfiguration import (
    DEFAULT_PROVIDER_SCOPES,
    ProviderConfiguration,
)
from app.services.provider_sync import grouped_imported_data, latest_successful_import, sync_provider_configuration


provider_configurations = Blueprint("provider_configurations", __name__)
REQUIRED_SYNC_SCOPES = DEFAULT_PROVIDER_SCOPES.split()


def _json_error(message: str, status_code: int):
    return {"error": message}, status_code


def _normalized_scopes(scopes) -> str:
    normalized_scopes: list[str] = []

    if isinstance(scopes, list):
        normalized_scopes = [str(scope).strip() for scope in scopes if str(scope).strip()]
    elif isinstance(scopes, str) and scopes.strip():
        normalized_scopes = [scope for scope in scopes.split() if scope]

    if not normalized_scopes:
        normalized_scopes = REQUIRED_SYNC_SCOPES.copy()

    for scope in REQUIRED_SYNC_SCOPES:
        if scope not in normalized_scopes:
            normalized_scopes.append(scope)

    return " ".join(normalized_scopes)


@provider_configurations.route("/provider-configurations", methods=["POST"])
def create_provider_configuration():
    payload = request.get_json(silent=True) or {}

    name = str(payload.get("name") or "").strip()
    base_url = str(payload.get("baseUrl") or payload.get("base_url") or "").strip().rstrip("/")
    token_url = str(payload.get("tokenUrl") or payload.get("token_url") or "").strip().rstrip("/")
    client_id = str(payload.get("clientId") or payload.get("client_id") or "").strip()
    client_secret = str(payload.get("clientSecret") or payload.get("client_secret") or "").strip()
    scopes = payload.get("scopes")

    if not name:
        return _json_error("name is required", 400)
    if not base_url:
        return _json_error("baseUrl is required", 400)
    if not client_id:
        return _json_error("clientId is required", 400)
    if not client_secret:
        return _json_error("clientSecret is required", 400)

    scopes_text = _normalized_scopes(scopes)

    configuration = ProviderConfiguration(
        name=name,
        base_url=base_url,
        token_url=token_url or None,
        client_id=client_id,
        client_secret=client_secret,
        scopes_text=scopes_text,
    )
    db.session.add(configuration)
    db.session.commit()

    return {"providerConfiguration": configuration.to_dict()}, 201


@provider_configurations.route("/provider-configurations/<int:config_id>/sync", methods=["POST"])
def sync_provider_configuration_route(config_id: int):
    configuration = ProviderConfiguration.query.get(config_id)
    if not configuration:
        return _json_error("Provider configuration not found", 404)

    try:
        import_run = sync_provider_configuration(configuration)
    except Exception as exc:
        return _json_error(str(exc), 502)

    return {
        "providerConfiguration": configuration.to_dict(),
        "providerImportRun": import_run.to_dict(),
    }, 200


@provider_configurations.route("/provider-configurations/<int:config_id>/data", methods=["GET"])
def get_imported_provider_data(config_id: int):
    configuration = ProviderConfiguration.query.get(config_id)
    if not configuration:
        return _json_error("Provider configuration not found", 404)

    import_run = latest_successful_import(config_id)
    if not import_run:
        return _json_error("No imported dataset exists for this provider configuration", 404)

    requested_resource = str(request.args.get("resource") or "").strip()
    data = grouped_imported_data(import_run.id)

    if requested_resource:
        if requested_resource not in data:
            return _json_error("Requested resource is not available in the imported dataset", 404)
        return {
            "providerConfiguration": configuration.to_dict(),
            "providerImportRun": import_run.to_dict(),
            "resource": requested_resource,
            "count": len(data[requested_resource]),
            "data": data[requested_resource],
        }

    return {
        "providerConfiguration": configuration.to_dict(),
        "providerImportRun": import_run.to_dict(),
        "data": data,
    }
