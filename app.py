from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request

app = Flask(__name__)

DATA_FILE = Path(__file__).with_name("strength.json")
AUTH_KEY = "ThisD0y"


@app.post("/update_daily_strength")
def update_daily_strength() -> Response:
    auth_key = request.args.get("auth_key")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
