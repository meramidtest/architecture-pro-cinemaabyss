from flask import Flask, jsonify, request
from kafka import KafkaProducer
import os
import json

app = Flask(__name__)

@app.route("/api/events/health", methods=["GET"])
def api_health():
    return jsonify(status=True), 200

@app.route("/api/events/movie", methods=["POST"])
def create_movie_event():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(status="error", message="Invalid JSON"), 400
        producer.send('movie-events', json.dumps(payload).encode("utf-8"))
        return jsonify(status="success"), 201
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 500

@app.route("/api/events/user", methods=["POST"])
def create_user_event():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(status="error", message="Invalid JSON"), 400
        producer.send('user-events', json.dumps(payload).encode("utf-8"))
        return jsonify(status="success"), 201
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 500

@app.route("/api/events/payment", methods=["POST"])
def create_payment_event():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(status="error", message="Invalid JSON"), 400
        producer.send('payment-events', json.dumps(payload).encode("utf-8"))
        return jsonify(status="success"), 201
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 500

@app.route("/health")
def health():
    producer.send('movie-events', b'some_message_bytes')
    return jsonify(status="ok"), 200

@app.route("/")
def index():
    return "Hello from Flask + Kafka consumer in one container!", 200

if __name__ == "__main__":
    global producer
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS") or os.environ.get("KAFKA_BROKERS") or "kafka:9092"
    producer = KafkaProducer(bootstrap_servers=bootstrap, api_version=(2, 7, 0))
    app.run(host="0.0.0.0", port=8082)
