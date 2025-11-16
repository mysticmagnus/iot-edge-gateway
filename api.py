import sqlite3
import datetime
from datetime import timezone
from flask import Flask, request, jsonify

# Create the Flask application object
app = Flask(__name__)
DB_FILE = 'readings.db'


def get_db_connection():
    """Helper function to connect to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn


# --- API Endpoint 1: POST (Write) Data ---
@app.route('/api/readings', methods=['POST'])
def add_reading():
    """
    API endpoint to add a new sensor reading.
    Expects JSON: { "value": <int> }
    """
    # 1. Get the JSON data from the request
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # 2. Validate the data
    if 'value' not in data or not isinstance(data['value'], int):
        return jsonify({"error": "Missing or invalid 'value' key"}), 400

    pot_value = data['value']
    timestamp = datetime.datetime.utcnow().isoformat()

    # 3. Insert into database
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO readings (timestamp, pot_value) VALUES (?, ?)',
            (timestamp, pot_value)
        )
        conn.commit()
        conn.close()

        # 4. Send a success response
        response = {
            "status": "success",
            "message": "Data logged",
            "logged_data": {
                "timestamp": timestamp,
                "pot_value": pot_value
            }
        }
        return jsonify(response), 201  # 201 = "Created"

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


# --- API Endpoint 2: GET (Read) Data ---
@app.route('/api/readings/latest', methods=['GET'])
def get_latest_reading():
    """
    API endpoint to retrieve the most recent sensor reading.
    """
    try:
        conn = get_db_connection()
        # Find the single most recent row
        cursor = conn.execute('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1')
        reading = cursor.fetchone()
        conn.close()

        if reading is None:
            return jsonify({"error": "No data available"}), 404

        # Convert the sqlite3.Row object to a standard dictionary
        response_data = dict(reading)
        return jsonify(response_data), 200  # 200 = "OK"

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


# --- Run the application ---
if __name__ == '__main__':
    # 'host="0.0.0.0"' makes the API accessible from
    # any computer on your network, not just the Pi itself.
    app.run(host='0.0.0.0', port=5000, debug=True)
