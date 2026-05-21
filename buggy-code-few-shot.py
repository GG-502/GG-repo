from flask import Flask, request, g, jsonify
import sqlite3


app = Flask(__name__)
app.config['DATABASE'] = 'users.db'


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
    if user_id is None:
        return jsonify({"error": "Missing or invalid 'id' parameter"}), 400

    db = get_db()
    try:
        cursor = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
    except sqlite3.DatabaseError:
        app.logger.exception("Database error while fetching user %s", user_id)
        return jsonify({"error": "Internal database error"}), 500

    if user_data is None:
        return jsonify({"error": "User not found"}), 404

    user_profile = process_data(user_data)
    formatted_response = format_response(user_profile)

    if isinstance(formatted_response, (dict, list)):
        return jsonify(formatted_response)
    return formatted_response


# (Assume process_data and format_response exist elsewhere)
