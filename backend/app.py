from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "DermaAI backend is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)