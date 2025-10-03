import os
import random
from urllib.parse import urljoin

import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Environment configuration
PORT = int(os.getenv("PORT", "8000"))
MONOLITH_URL = os.getenv("MONOLITH_URL", "http://monolith:8080")
MOVIES_SERVICE_URL = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
EVENTS_SERVICE_URL = os.getenv("EVENTS_SERVICE_URL", "http://events-service:8082")
GRADUAL_MIGRATION = os.getenv("GRADUAL_MIGRATION", "false").lower() in ("1", "true", "yes", "on")
MOVIES_MIGRATION_PERCENT = int(os.getenv("MOVIES_MIGRATION_PERCENT", "0"))

# Clamp migration percentage to [0, 100]
if MOVIES_MIGRATION_PERCENT < 0:
  MOVIES_MIGRATION_PERCENT = 0
if MOVIES_MIGRATION_PERCENT > 100:
  MOVIES_MIGRATION_PERCENT = 100


def choose_movies_upstream() -> str:
  """Decide where to route movies traffic based on feature flag and percentage."""
  if not GRADUAL_MIGRATION:
    return MONOLITH_URL
  # Sample per request
  roll = random.randint(1, 100)
  if roll <= MOVIES_MIGRATION_PERCENT:
    return MOVIES_SERVICE_URL
  return MONOLITH_URL


def build_outgoing_headers() -> dict:
  # Forward most headers except hop-by-hop or calculated ones
  excluded = {"host", "content-length", "connection", "accept-encoding"}
  return {k: v for k, v in request.headers.items() if k.lower() not in excluded}


def make_flask_response(upstream_resp: requests.Response) -> Response:
  excluded = {"content-encoding", "transfer-encoding", "connection"}
  headers = [(k, v) for k, v in upstream_resp.headers.items() if k.lower() not in excluded]
  return Response(response=upstream_resp.content, status=upstream_resp.status_code, headers=headers)


def forward_to(upstream_base: str) -> Response:
  url = upstream_base + request.path
  resp = requests.request(
    method=request.method,
    url=url,
    params=request.args,
    headers=build_outgoing_headers(),
    data=request.get_data(),
    cookies=request.cookies,
    allow_redirects=False,
    timeout=15,
  )
  return make_flask_response(resp)


@app.route("/health", methods=["GET"])  # Simple health endpoint
def health():
  return jsonify({"status": True})


# Movies endpoints → routed conditionally between monolith and movies service
@app.route("/api/movies", methods=["GET", "POST"])  
def proxy_movies():
  upstream = choose_movies_upstream()
  return forward_to(upstream)


# Users, payments, subscriptions → stay on monolith
@app.route("/api/users", methods=["GET", "POST"]) 
@app.route("/api/payments", methods=["GET", "POST"]) 
@app.route("/api/subscriptions", methods=["GET", "POST"]) 
def proxy_monolith_only():
  return forward_to(MONOLITH_URL)


# Events endpoints → always to events service
@app.route("/api/events", methods=["GET", "POST"]) 
@app.route("/api/events/<path:subpath>", methods=["GET", "POST"]) 
def proxy_events(subpath: str = ""):
  return forward_to(EVENTS_SERVICE_URL)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=PORT) 