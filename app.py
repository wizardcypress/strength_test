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
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"<title>{escape(title)}</title>",
        "<style>",
        "body {",
        "  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;",
        "  margin: 0;",
        "  padding: 24px;",
        "  background-color: #f4f5f7;",
        "  color: #1f2933;",
        "}",
        "h1 {",
        "  font-size: 2rem;",
        "  margin-bottom: 16px;",
        "}",
        ".page {",
        "  max-width: 960px;",
        "  margin: 0 auto;",
        "}",
        ".table-container {",
        "  background: #ffffff;",
        "  border-radius: 12px;",
        "  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);",
        "  overflow-x: auto;",
        "}",
        "table {",
        "  width: 100%;",
        "  border-collapse: collapse;",
        "  min-width: 400px;",
        "}",
        "thead {",
        "  background: linear-gradient(135deg, #2563eb, #38bdf8);",
        "  color: #ffffff;",
        "}",
        "th, td {",
        "  text-align: left;",
        "  padding: 12px 16px;",
        "  border-bottom: 1px solid #e5e7eb;",
        "  white-space: nowrap;",
        "}",
        "tbody tr:nth-child(even) {",
        "  background-color: #f8fafc;",
        "}",
        "tbody tr:hover {",
        "  background-color: #e0f2fe;",
        "}",
        "@media (max-width: 768px) {",
        "  body {",
        "    padding: 16px;",
        "  }",
        "  h1 {",
        "    font-size: 1.5rem;",
        "    margin-bottom: 12px;",
        "  }",
        "  .table-container {",
        "    border-radius: 10px;",
        "    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12);",
        "  }",
        "  table {",
        "    min-width: auto;",
        "  }",
        "  th, td {",
        "    padding: 10px 12px;",
        "    font-size: 0.95rem;",
        "  }",
        "}",
        "@media (max-width: 480px) {",
        "  body {",
        "    padding: 12px;",
        "  }",
        "  h1 {",
        "    font-size: 1.35rem;",
        "  }",
        "  th, td {",
        "    padding: 8px 10px;",
        "    font-size: 0.9rem;",
        "  }",
        "  .page {",
        "    width: 100%;",
        "  }",
        "}",
        "</style>",
        "</head>",
        "<body>",
        "<div class=\"page\">",
        f"<h1>{escape(title)}</h1>",
        "<div class=\"table-container\">",
        "<table>",
    ]

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
    html_parts.append("</div>")
    html_parts.append("</div>")
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
