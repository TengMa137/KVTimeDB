from flask import Flask, request, jsonify
from database import KVDatabase
import atexit
import sqlite3

app = Flask(__name__)

# Initialize database with 10 second timeout
db = KVDatabase('store.db', timeout=10.0)

# Clean up on exit
atexit.register(db.close)

@app.route("/", methods=["PUT"])
def put():
    """Store key-value pair with timestamp"""
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['key', 'value', 'timestamp']):
        return jsonify({'error': 'Missing required fields: key, value, timestamp'}), 400
    
    try:
        key = str(data['key'])
        value = str(data['value'])
        timestamp = int(data['timestamp'])
        
        db.put(key, timestamp, value)
        return '', 200
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data types: {str(e)}'}), 400
    except sqlite3.OperationalError as e:
        if "busy" in str(e) or "locked" in str(e):
            return jsonify({'error': 'Database temporarily unavailable, try again'}), 503
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route("/", methods=["GET"])
def get():
    """Get value for key at or before given timestamp"""
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['key', 'timestamp']):
        return jsonify({'error': 'Missing required fields: key, timestamp'}), 400
    
    try:
        key = str(data['key'])
        timestamp = int(data['timestamp'])
        
        value = db.get(key, timestamp)
        return jsonify(value), 200
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data types: {str(e)}'}), 400
    except sqlite3.OperationalError as e:
        if "busy" in str(e) or "locked" in str(e):
            return jsonify({'error': 'Database temporarily unavailable, try again'}), 503
        return jsonify({'error': f'Database error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, threaded=True)