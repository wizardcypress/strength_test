from __future__ import annotations

import csv
from html import escape
from io import StringIO
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

    raw_text = DATA_FILE.read_text(encoding="utf-8")
    lines = [line for line in raw_text.splitlines() if line.strip()]
    if not lines:
        abort(500, description="strength data missing title")

    title = lines[0]
    csv_content = "\n".join(lines[1:])

    rows: list[list[str]] = []
    if csv_content:
        reader = csv.reader(StringIO(csv_content))
        rows = list(reader)

    html_parts: list[str] = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset=\"utf-8\">",
        f"<title>{escape(title)}</title>",
        "</head>",
        "<body>",
        f"<h1>{escape(title)}</h1>",
    ]

    html_parts.append("<table border=\"1\" cellspacing=\"0\" cellpadding=\"4\">")
    if rows:
        header, *body_rows = rows
        html_parts.append("<thead>")
        html_parts.append("<tr>")
        for cell in header:
            html_parts.append(f"<th>{escape(cell)}</th>")
        html_parts.append("</tr>")
        html_parts.append("</thead>")

        html_parts.append("<tbody>")
        for row in body_rows:
            html_parts.append("<tr>")
            for cell in row:
                html_parts.append(f"<td>{escape(cell)}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody>")
    else:
        html_parts.append("<tbody><tr><td><em>No data available</em></td></tr></tbody>")

    html_parts.append("</table>")
    html_parts.append("</body>")
    html_parts.append("</html>")

    html_output = "".join(html_parts)
    return Response(html_output, mimetype="text/html")


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
