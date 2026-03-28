import os
from flask import Flask, jsonify, request, send_from_directory

from database import fetch_messages, init_db, insert_message


app = Flask(__name__, static_folder=".", static_url_path="")


def _admin_authorized():
    secret = (os.getenv("ADMIN_SECRET") or "").strip()
    if not secret:
        return True
    got = (
        request.headers.get("X-Admin-Secret")
        or request.args.get("secret")
        or ""
    ).strip()
    return got == secret


def _serialize_message(row):
    m = dict(row)
    ca = m.get("created_at")
    if ca is not None:
        m["created_at"] = (
            ca.isoformat() if hasattr(ca, "isoformat") else str(ca)
        )
    return m


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


@app.route("/admin")
def admin_page():
    return send_from_directory(".", "admin.html")


@app.route("/api/admin/messages", methods=["GET"])
def admin_messages():
    if not _admin_authorized():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        _ensure_db_initialized()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    messages = [_serialize_message(m) for m in fetch_messages()]
    return jsonify({"messages": messages})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
