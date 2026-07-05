from flask import Blueprint, request, jsonify, send_from_directory, abort, Response
from flask import current_app as app
frontend = Blueprint('frontend', __name__)
import requests
from pathlib import Path


DIST_DIR = Path(__file__).resolve().parents[2] / "OneRoster-Frontend" / "dist"

PRODUCTS_DIR = Path(__file__).resolve().parents[2] / "public" / "products"


# this will be the api proxy route
@frontend.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def api_proxy(path):
    target_url = f'{app.config["API_BACKEND_URL"]}/{path}'
    if request.method == "GET":
        response = requests.get(target_url, headers=request.headers, allow_redirects=False)
    elif request.method == "POST":
        data = request.get_json(silent=True)
        response = requests.post(target_url, json=data, data=None if data is not None else request.get_data(), headers=request.headers, allow_redirects=False)
    elif request.method == "PUT":
        data = request.get_json(silent=True)
        response = requests.put(target_url, json=data, data=None if data is not None else request.get_data(), headers=request.headers, allow_redirects=False)
    elif request.method == "DELETE":
        response = requests.delete(target_url, headers=request.headers, allow_redirects=False)
    else:
        return jsonify({"error": "Method not allowed"}), 405

    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}

    raw_headers = getattr(response.raw, "headers", None)
    if raw_headers is not None and hasattr(raw_headers, "getlist"):
        set_cookies = raw_headers.getlist("Set-Cookie")
    elif raw_headers is not None and hasattr(raw_headers, "get_all"):
        set_cookies = raw_headers.get_all("Set-Cookie") or []
    else:
        set_cookies = []

    print("PROXY status:", response.status_code)
    print("PROXY upstream Location:", response.headers.get("Location"))
    print("PROXY upstream Set-Cookie(s):", set_cookies)

    resp = Response(response.content, response.status_code)

    for k, v in response.headers.items():
        if k.lower() not in excluded and k.lower() != "set-cookie":
            resp.headers[k] = v

    seen = set()
    for c in set_cookies:
        if c and c not in seen:
            resp.headers.add("Set-Cookie", c)
            seen.add(c)

    print("PROXY outgoing Set-Cookie(s):", resp.headers.getlist("Set-Cookie"))
    return resp



@frontend.route("/", defaults={"path": ""})
@frontend.route("/<path:path>")
def serve(path):
    target = DIST_DIR / path
    if path and target.exists() and target.is_file():
        return send_from_directory(DIST_DIR, path)
    index = DIST_DIR / "index.html"
    if index.exists():
        return send_from_directory(DIST_DIR, "index.html")
    abort(404)
    
@frontend.route("/products/<path:product_path>")
def serve_products(product_path):
    if not product_path.endswith(".html"):
        product_path = f"{product_path}.html"
    return send_from_directory(PRODUCTS_DIR, product_path)
