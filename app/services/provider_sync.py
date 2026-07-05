import base64
from collections import defaultdict
from datetime import datetime

import requests

from app import db
from app.models.ImportedRecord import ImportedRecord
from app.models.ProviderConfiguration import ProviderConfiguration
from app.models.ProviderImportRun import ProviderImportRun


COLLECTION_ENDPOINTS = {
    "academicSessions": "academicSessions",
    "classes": "classes",
    "courses": "courses",
    "demographics": "demographics",
    "enrollments": "enrollments",
    "gradingPeriods": "gradingPeriods",
    "orgs": "orgs",
    "schools": "schools",
    "students": "students",
    "teachers": "teachers",
    "terms": "terms",
    "users": "users",
}

PAGE_LIMIT = 100
REQUEST_TIMEOUT = 30


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _parse_json_response(response: requests.Response, fallback: str) -> dict:
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(fallback) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(fallback)
    return payload


def _issue_provider_token(configuration: ProviderConfiguration) -> str:
    basic = base64.b64encode(
        f"{configuration.client_id}:{configuration.client_secret}".encode("utf-8")
    ).decode("utf-8")
    response = requests.post(
        configuration.resolved_token_url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {basic}",
        },
        data={
            "grant_type": "client_credentials",
            "scope": configuration.scopes_text,
        },
        timeout=REQUEST_TIMEOUT,
    )
    if not response.ok:
        raise RuntimeError(
            f"Token request failed with status {response.status_code}: {response.text[:300]}"
        )

    payload = _parse_json_response(response, "Token response was not valid JSON.")
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("Token response did not contain an access_token.")
    return access_token


def _fetch_collection(
    configuration: ProviderConfiguration,
    access_token: str,
    endpoint: str,
    response_key: str,
) -> list[dict]:
    offset = 0
    collected_records: list[dict] = []

    while True:
        response = requests.get(
            _join_url(configuration.base_url, endpoint),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            params={
                "limit": PAGE_LIMIT,
                "offset": offset,
            },
            timeout=REQUEST_TIMEOUT,
        )
        if not response.ok:
            raise RuntimeError(
                f"Provider request for {endpoint} failed with status {response.status_code}: {response.text[:300]}"
            )

        payload = _parse_json_response(
            response,
            f"Provider response for {endpoint} was not valid JSON.",
        )
        records = payload.get(response_key)
        if not isinstance(records, list):
            raise RuntimeError(f"Provider response for {endpoint} did not include a {response_key} collection.")

        collected_records.extend(record for record in records if isinstance(record, dict))

        if len(records) < PAGE_LIMIT:
            break
        offset += PAGE_LIMIT

    return collected_records


def sync_provider_configuration(configuration: ProviderConfiguration) -> ProviderImportRun:
    import_run = ProviderImportRun(
        provider_configuration_id=configuration.id,
        status="running",
        started_at=datetime.utcnow(),
        counts_json={},
    )
    db.session.add(import_run)
    db.session.commit()

    try:
        access_token = _issue_provider_token(configuration)
        counts: dict[str, int] = {}
        imported_records: list[ImportedRecord] = []

        for resource_type, endpoint in COLLECTION_ENDPOINTS.items():
            records = _fetch_collection(configuration, access_token, endpoint, resource_type)
            counts[resource_type] = len(records)

            for record in records:
                sourced_id = str(record.get("sourcedId") or "")
                if not sourced_id:
                    raise RuntimeError(
                        f"Provider returned a {resource_type} record without sourcedId."
                    )
                imported_records.append(
                    ImportedRecord(
                        provider_configuration_id=configuration.id,
                        import_run_id=import_run.id,
                        resource_type=resource_type,
                        sourced_id=sourced_id,
                        payload_json=record,
                    )
                )

        db.session.add_all(imported_records)
        import_run.status = "succeeded"
        import_run.finished_at = datetime.utcnow()
        import_run.error_message = None
        import_run.counts_json = counts
        db.session.commit()
        return import_run
    except Exception as exc:
        db.session.rollback()
        failed_run = ProviderImportRun.query.get(import_run.id)
        if failed_run:
            failed_run.status = "failed"
            failed_run.finished_at = datetime.utcnow()
            failed_run.error_message = str(exc)
            db.session.commit()
        raise


def latest_successful_import(configuration_id: int) -> ProviderImportRun | None:
    return (
        ProviderImportRun.query.filter_by(
            provider_configuration_id=configuration_id,
            status="succeeded",
        )
        .order_by(ProviderImportRun.started_at.desc(), ProviderImportRun.id.desc())
        .first()
    )


def grouped_imported_data(import_run_id: int) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    records = (
        ImportedRecord.query.filter_by(import_run_id=import_run_id)
        .order_by(ImportedRecord.resource_type.asc(), ImportedRecord.sourced_id.asc())
        .all()
    )
    for record in records:
        grouped[record.resource_type].append(record.payload_json)
    return dict(grouped)
