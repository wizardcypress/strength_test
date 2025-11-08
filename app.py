from __future__ import annotations

from pathlib import Path

from flask import Flask, Response, abort, request

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

    payload = request.get_data(as_text=True)
    if not payload:
        abort(400, description="Request body must be non-empty text")

    DATA_FILE.write_text(payload, encoding="utf-8")
    return Response("success", mimetype="text/plain")


@app.get("/daily_strength/get")
def get_daily_strength() -> Response:
    if not DATA_FILE.exists():
        abort(404, description="strength data not found")

    data = DATA_FILE.read_text(encoding="utf-8")
    return Response(data, mimetype="text/plain")


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
