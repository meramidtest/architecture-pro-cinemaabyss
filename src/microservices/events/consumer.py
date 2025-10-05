from kafka import KafkaConsumer
import signal
import time
import os

RUNNING = True

def handle_sigterm(signum, frame):
    global RUNNING
    RUNNING = False

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS") or os.environ.get("KAFKA_BROKERS") or "kafka:9092"


if __name__ == '__main__':
    consumer = KafkaConsumer(
        'movie-events', 'user-events', 'payment-events',
        group_id='events',
        bootstrap_servers=bootstrap,
        api_version=(2, 7, 0),
    )

    try:
        while RUNNING:
            for msg in consumer:
                print(f"[consumer] {msg.topic}@{msg.partition} #{msg.offset}: {msg.value.decode('utf-8', errors='ignore')}", flush=True)
                if not RUNNING:
                    break

                time.sleep(0.2)
    finally:
        try:
            consumer.close()
        except Exception:
            pass

    print("[consumer] shutdown complete", flush=True)