import os
from flask import Flask, jsonify, request, send_from_directory

from database import fetch_messages, init_db, insert_message


app = Flask(__name__, static_folder=".", static_url_path="")

def _ensure_db_initialized():
    if getattr(app, "_db_initialized", False):
        return
    init_db()
    app._db_initialized = True


@app.route("/")
def root():
    return send_from_directory(".", "index.html")


@app.route("/health")
def health():
    db_ok = True
    db_error = None
    try:
        _ensure_db_initialized()
    except Exception as exc:
        db_ok = False
        db_error = str(exc)
    return jsonify({"status": "ok", "db_ok": db_ok, "db_error": db_error})


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"error": "name, email and message are required"}), 400

    if "@" not in email:
        return jsonify({"error": "please provide a valid email"}), 400

    try:
        _ensure_db_initialized()
    except Exception:
        return jsonify({"error": "Database is not configured. Set DATABASE_URL and try again."}), 500

    row = insert_message(name=name, email=email, message=message)
    return jsonify({"message": "saved", "id": row["id"], "created_at": str(row["created_at"])})


@app.route("/admin", methods=["GET"])
def admin():
    try:
        _ensure_db_initialized()
    except Exception as exc:
        return (
            "<h2>Database not configured</h2>"
            "<p>Set <b>DATABASE_URL</b> (PostgreSQL) and restart the server.</p>"
            f"<pre>{exc}</pre>",
            500,
        )

    messages = fetch_messages()

    rows = []
    for msg in messages:
        rows.append(
            "<tr>"
            f"<td>{msg['id']}</td>"
            f"<td>{msg['name']}</td>"
            f"<td>{msg['email']}</td>"
            f"<td>{msg['message']}</td>"
            f"<td>{msg['created_at']}</td>"
            "</tr>"
        )

    html = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Admin</title>"
        "<style>body{font-family:Arial;margin:30px;background:#111;color:#fff;}"
        "table{border-collapse:collapse;width:100%;background:#1a1a1a;}"
        "th,td{border:1px solid #333;padding:10px;text-align:left;}"
        "th{background:#222;}h1{color:#00cfff;}</style></head><body>"
        "<h1>Contact Messages</h1>"
        "<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Message</th><th>Created At</th></tr></thead>"
        f"<tbody>{''.join(rows) if rows else '<tr><td colspan=5>No messages yet.</td></tr>'}</tbody>"
        "</table></body></html>"
    )
    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
