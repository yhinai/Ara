"""Vercel Python serverless function: /api/check

Polls Stripe for paid checkout sessions tied to a payment link.

Query params:
  link_id  (required) Stripe Payment Link id (plink_...)
  since    (optional) Unix seconds; only count sessions created >= this value

Response:
  200  {"count": <int>, "link_id": "<str>"}
  4xx  {"error": "<message>"}

Uses only the Python standard library (urllib). STRIPE_SECRET_KEY env var required.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler


STRIPE_API = "https://api.stripe.com/v1/checkout/sessions"


def _fetch_sessions(link_id: str, secret_key: str) -> list[dict]:
    query = urllib.parse.urlencode({"limit": "100", "payment_link": link_id})
    request = urllib.request.Request(
        f"{STRIPE_API}?{query}",
        headers={"Authorization": f"Bearer {secret_key}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body.get("data", []) or []


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 (Vercel requires lowercase handler)
        try:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            link_id = (params.get("link_id") or [""])[0].strip()
            if not link_id:
                self._send_json(400, {"error": "Missing required query param: link_id"})
                return

            since_raw = (params.get("since") or [""])[0].strip()
            since = 0
            if since_raw:
                try:
                    since = int(float(since_raw))
                except ValueError:
                    self._send_json(400, {"error": "since must be a unix timestamp"})
                    return

            secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
            if not secret_key:
                self._send_json(500, {"error": "STRIPE_SECRET_KEY env var not configured"})
                return

            sessions = _fetch_sessions(link_id, secret_key)
            count = 0
            for session in sessions:
                if session.get("payment_status") != "paid":
                    continue
                created = int(session.get("created") or 0)
                if since and created < since:
                    continue
                count += 1

            self._send_json(200, {"count": count, "link_id": link_id})
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("error", {}).get("message")
            except Exception:
                detail = None
            self._send_json(exc.code, {"error": detail or f"Stripe HTTP {exc.code}"})
        except urllib.error.URLError as exc:
            self._send_json(502, {"error": f"Upstream connection failed: {exc.reason}"})
        except Exception as exc:  # noqa: BLE001 (last-resort guard)
            self._send_json(500, {"error": f"Unexpected error: {exc.__class__.__name__}"})
