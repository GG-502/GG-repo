import os
from flask import Flask, request, g, abort, jsonify
import sqlite3


app = Flask(__name__)
# Ensure the instance folder exists (prevents sqlite path errors)
os.makedirs(app.instance_path, exist_ok=True)
# Default DB lives in the instance folder; override via config in production.
app.config.setdefault('DATABASE', os.path.join(app.instance_path, 'users.db'))


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/user')
def get_user_profile():
    user_id = request.args.get('id', type=int)
    if user_id is None or user_id <= 0:
        abort(400, description="Missing or invalid 'id' parameter")

    try:
        db = get_db()
        cursor = db.execute(
            "SELECT user_id, username, email FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
    except sqlite3.Error as e:
        app.logger.exception("Database error while fetching user %s", user_id)
        abort(500, description="Internal server error")

    if not row:
        abort(404, description="User not found")

    user_data = dict(row)
    temp = process_data(user_data)
    res = format_response(temp)
    return res


def process_data(user_data: dict) -> dict:
    # Minimal processing: remove or redact sensitive fields before exposing.
    # In production, expand filtering/formatting and enforce auth checks.
    user = dict(user_data)
    user.pop('email', None)  # redact email by default
    return user


def format_response(data: dict):
    # Return a JSON response; caller can replace with a richer formatter.
    return jsonify(data)
