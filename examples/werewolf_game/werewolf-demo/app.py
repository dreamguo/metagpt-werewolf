from flask import Flask, jsonify
from flask_cors import CORS
from parse_log import parse_log_file  # Import your existing parse function
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/game-data', methods=['GET'])
def get_game_data():
    try:
        # Assuming output.log is in the same directory as this script
        game_data = parse_log_file("output.log")
        return jsonify(game_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
