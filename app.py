from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request

AUTH_KEY: str | None = None

app = Flask(__name__)

DATA_FILE = Path(__file__).with_name("strength.json")


@app.post("/update_daily_strength")
def update_daily_strength() -> Response:
    auth_key = request.args.get("auth_key")
    if AUTH_KEY is None:
        abort(500, description="Auth key not configured")

    if auth_key != AUTH_KEY:
        abort(403, description="Invalid auth key")

    payload = request.get_json(silent=True)
    if payload is None:
        abort(400, description="Request body must be valid JSON")

    DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify({"status": "success"})


@app.get("/daily_strength/get")
def get_daily_strength() -> Response:
    if not DATA_FILE.exists():
        abort(404, description="strength data not found")

    with DATA_FILE.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    return jsonify(data)


def set_auth_key(value: str) -> None:
    global AUTH_KEY
    AUTH_KEY = value


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the daily strength Flask app.")
    parser.add_argument("--auth-key", required=True, help="Authentication key for update endpoint")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    set_auth_key(args.auth_key)
    app.run(host=args.host, port=args.port, debug=args.debug)
