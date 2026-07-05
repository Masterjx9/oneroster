import re
from string import Template

from flask import Blueprint, current_app, jsonify, render_template_string


docs_routes = Blueprint("docs_routes", __name__)


SWAGGER_UI_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>OneRoster API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
      html { box-sizing: border-box; overflow-y: scroll; }
      *, *:before, *:after { box-sizing: inherit; }
      body { margin: 0; background: #f8fafc; }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
      window.onload = function() {
        window.ui = SwaggerUIBundle({
          url: "$openapi_url",
          dom_id: '#swagger-ui',
          deepLinking: true,
          docExpansion: 'list',
          displayOperationId: true,
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          layout: "BaseLayout"
        });
      };
    </script>
  </body>
</html>
"""
)


def _strip_prefix(path: str, prefix: str) -> str:
    if path.startswith(prefix):
        path = path[len(prefix):]
    return path or "/"


def _to_openapi_path(path: str) -> str:
    return re.sub(r"<(?:[^:>]+:)?([^>]+)>", r"{\1}", path)


def _humanize_operation(name: str) -> str:
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name).replace("_", " ")
    return words[:1].upper() + words[1:]


def _ordered_path_params(rule_text: str) -> list[str]:
    return re.findall(r"<(?:[^:>]+:)?([^>]+)>", rule_text)


def _path_parameters(rule_text: str) -> list[dict]:
    return [
        {
            "name": param,
            "in": "path",
            "required": True,
            "schema": {"type": "string"},
        }
        for param in _ordered_path_params(rule_text)
    ]


def _collection_query_parameters(openapi_path: str, method: str) -> list[dict]:
    if method != "GET" or openapi_path.endswith("}"):
        return []

    return [
        {
            "name": "limit",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "default": 100, "minimum": 1},
        },
        {
            "name": "offset",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "default": 0, "minimum": 0},
        },
        {
            "name": "sort",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
        },
        {
            "name": "orderBy",
            "in": "query",
            "required": False,
            "schema": {"type": "string", "enum": ["asc", "desc"]},
        },
        {
            "name": "filter",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
        },
        {
            "name": "fields",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
        },
    ]


def _build_operation(rule, method: str, url_prefix: str) -> dict:
    endpoint_name = rule.endpoint.split(".")[-1]
    openapi_path = _to_openapi_path(_strip_prefix(rule.rule, url_prefix))
    parameters = _path_parameters(rule.rule)
    parameters.extend(_collection_query_parameters(openapi_path, method))

    operation = {
        "operationId": endpoint_name,
        "summary": _humanize_operation(endpoint_name),
        "responses": {
            "200": {"description": "Successful response"},
            "401": {"description": "Unauthorized"},
            "403": {"description": "Forbidden"},
            "404": {"description": "Not found"},
        },
    }

    if parameters:
        operation["parameters"] = parameters

    if endpoint_name != "issue_token":
        operation["security"] = [{"bearerAuth": []}, {"oauth1Auth": []}]

    if endpoint_name == "issue_token":
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "required": ["grant_type", "scope"],
                        "properties": {
                            "grant_type": {"type": "string", "example": "client_credentials"},
                            "scope": {"type": "string"},
                        },
                    }
                }
            },
        }
    elif method == "PUT":
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "additionalProperties": True,
                    }
                }
            },
        }

    return operation


def _build_openapi_spec() -> dict:
    from app import url_prefix

    paths: dict[str, dict] = {}
    excluded_endpoints = {"docs_routes.swagger_ui", "docs_routes.openapi_json"}

    for rule in sorted(current_app.url_map.iter_rules(), key=lambda item: item.rule):
        if not rule.rule.startswith(url_prefix):
            continue
        if rule.endpoint in excluded_endpoints:
            continue

        openapi_path = _to_openapi_path(_strip_prefix(rule.rule, url_prefix))
        methods = sorted(method for method in rule.methods if method not in {"HEAD", "OPTIONS"})

        if not methods:
            continue

        path_item = paths.setdefault(openapi_path, {})
        for method in methods:
            path_item[method.lower()] = _build_operation(rule, method, url_prefix)

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "OneRoster API",
            "version": "1.0.0",
            "description": "Swagger UI for the OneRoster service.",
        },
        "servers": [{"url": url_prefix}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                },
                "oauth1Auth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "description": "OAuth 1.0a HMAC-SHA1 signed Authorization header.",
                }
            }
        },
        "paths": paths,
    }


@docs_routes.route("", methods=["GET"])
@docs_routes.route("/", methods=["GET"])
def swagger_ui():
    from app import url_prefix

    return render_template_string(
        SWAGGER_UI_TEMPLATE.substitute(openapi_url=f"{url_prefix}/openapi.json")
    )


@docs_routes.route("/openapi.json", methods=["GET"])
def openapi_json():
    return jsonify(_build_openapi_spec())
