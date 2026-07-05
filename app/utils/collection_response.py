from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import re
import json
from flask import jsonify, request

DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0
FILTER_PATTERN = re.compile(r"^\s*([A-Za-z0-9_.]+)\s*(<=|>=|!=|=|<|>|~)\s*'(.*)'\s*$")


def _get_field_value(item: dict, field_name: str):
    value = item
    for part in field_name.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value


def _field_exists(item: dict, field_name: str) -> bool:
    return _get_field_value(item, field_name) is not None or field_name in item


def _normalize_value(value):
    if isinstance(value, list):
        return [str(item).lower() for item in value]
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True).lower()
    if value is None:
        return None
    return str(value).lower()


def _matches_filter(item: dict, expression: str) -> bool:
    match = FILTER_PATTERN.match(expression)
    if not match:
        return False

    field_name, operator, raw_value = match.groups()
    value = _get_field_value(item, field_name)
    if value is None:
        return False

    normalized_value = _normalize_value(value)
    comparison_value = raw_value.lower()

    if isinstance(normalized_value, list):
        requested_values = [part.strip().lower() for part in raw_value.split(",")]
        if operator == "=":
            return normalized_value == requested_values
        if operator == "!=":
            return normalized_value != requested_values
        if operator == "~":
            return any(part in normalized_value for part in requested_values)
        return False

    if operator == "=":
        return normalized_value == comparison_value
    if operator == "!=":
        return normalized_value != comparison_value
    if operator == ">":
        return normalized_value > comparison_value
    if operator == ">=":
        return normalized_value >= comparison_value
    if operator == "<":
        return normalized_value < comparison_value
    if operator == "<=":
        return normalized_value <= comparison_value
    if operator == "~":
        return comparison_value in normalized_value
    return False


def _apply_filter(items: list[dict], filter_query: str | None) -> list[dict]:
    if not filter_query:
        return items
    if " AND " in filter_query:
        filters = filter_query.split(" AND ")
        return [item for item in items if all(_matches_filter(item, part) for part in filters)]
    if " OR " in filter_query:
        filters = filter_query.split(" OR ")
        return [item for item in items if any(_matches_filter(item, part) for part in filters)]
    return [item for item in items if _matches_filter(item, filter_query)]


def _apply_sort(items: list[dict], sort_field: str | None, order_by: str | None) -> list[dict]:
    if not items or not sort_field or not _field_exists(items[0], sort_field):
        return items
    reverse = (order_by or "asc").lower() == "desc"
    return sorted(
        items,
        key=lambda item: str(_normalize_value(_get_field_value(item, sort_field)) or ""),
        reverse=reverse,
    )


def _apply_fields(items: list[dict], fields_query: str | None) -> list[dict]:
    if not items or not fields_query:
        return items
    fields = [field.strip() for field in fields_query.split(",") if field.strip()]
    if not fields or any(not _field_exists(items[0], field) for field in fields):
        return items
    return [{field: _get_field_value(item, field) for field in fields} for item in items]


def _build_link_header(limit: int, offset: int, total_count: int) -> str:
    parts = urlsplit(request.url)
    params = dict(parse_qsl(parts.query, keep_blank_values=True))
    last_offset = ((max(total_count, 1) - 1) // limit) * limit

    def build_url(new_offset: int) -> str:
        params["limit"] = str(limit)
        params["offset"] = str(new_offset)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), parts.fragment))

    links = [f'<{build_url(0)}>; rel="first"', f'<{build_url(last_offset)}>; rel="last"']
    if offset > 0:
        links.append(f'<{build_url(max(0, offset - limit))}>; rel="prev"')
    if offset + limit < total_count:
        links.append(f'<{build_url(offset + limit)}>; rel="next"')
    return ", ".join(links)


def collection_response(collection_name: str, items: list[dict]):
    limit = max(request.args.get("limit", DEFAULT_LIMIT, type=int) or DEFAULT_LIMIT, 1)
    offset = max(request.args.get("offset", DEFAULT_OFFSET, type=int) or DEFAULT_OFFSET, 0)

    filtered_items = _apply_filter(items, request.args.get("filter"))
    sorted_items = _apply_sort(filtered_items, request.args.get("sort"), request.args.get("orderBy"))
    total_count = len(sorted_items)
    paginated_items = sorted_items[offset:offset + limit]
    selected_items = _apply_fields(paginated_items, request.args.get("fields"))

    response = jsonify({collection_name: selected_items})
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["Link"] = _build_link_header(limit, offset, total_count)
    return response
