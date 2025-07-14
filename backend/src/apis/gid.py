from __future__ import annotations

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.message_controller import MesageController
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
controller = MesageController(num_history=10)


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "service": "Chatbot RAG API", "timestamp": time.time()}
    )


@app.route("/get_message", methods=["POST"])
def get_message():
    try:
        data = request.get_json()
        if not data or "input" not in data:
            return jsonify({"error": "Missing 'input' field"}), 400

        start = time.time()
        response = controller.get_message(data.get("input", ""))

        return jsonify(
            {"response": response, "time": time.time() - start, "status": "success"}
        )
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/get_history", methods=["GET"])
def get_history():
    try:
        return jsonify(
            {
                "history": controller.get_history(),
                "count": len(controller.get_history()),
                "status": "success",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/delete_history", methods=["DELETE"])
def delete_history():
    try:
        message = controller.delete_history()
        return jsonify({"message": message, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/config", methods=["GET"])
def get_config():
    """Get current configuration"""
    return jsonify({"num_history": controller.num_history, "status": "success"})


@app.route("/config", methods=["POST"])
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        if "num_history" in data:
            controller.num_history = int(data["num_history"])

        return jsonify(
            {
                "message": "Configuration updated successfully",
                "num_history": controller.num_history,
                "status": "success",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/export_history", methods=["GET"])
def export_history():
    """Export chat history"""
    try:
        history = controller.get_history()
        return jsonify(
            {
                "history": history,
                "exported_at": time.time(),
                "count": len(history),
                "status": "success",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": "error"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": "error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
