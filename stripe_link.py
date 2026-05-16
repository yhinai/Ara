from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


STRIPE_PAYMENT_LINKS_URL = "https://api.stripe.com/v1/payment_links"
DRY_RUN_URL = "https://buy.stripe.com/test_demo_link"


def create_payment_link(product: str, amount_cents: int = 100, currency: str = "usd") -> dict[str, Any]:
    """Create a Stripe Payment Link, or return a deterministic dry-run result."""
    product = product.strip()
    if not product:
        raise ValueError("product name/idea is required")
    if amount_cents <= 0:
        raise ValueError("amount cents must be positive")

    currency = currency.strip().lower() or "usd"
    api_key = os.getenv("STRIPE_SECRET_KEY")
    live_enabled = os.getenv("COMPANY_LAUNCH_LIVE_STRIPE") == "1"

    if not live_enabled or not api_key:
        return {
            "mode": "dry_run",
            "url": DRY_RUN_URL,
            "product": product,
            "amount_cents": amount_cents,
            "currency": currency,
            "note": "Set COMPANY_LAUNCH_LIVE_STRIPE=1 and STRIPE_SECRET_KEY to create a real Stripe Payment Link.",
        }

    payload = {
        "line_items[0][price_data][currency]": currency,
        "line_items[0][price_data][unit_amount]": str(amount_cents),
        "line_items[0][price_data][product_data][name]": product,
        "line_items[0][quantity]": "1",
        "metadata[demo]": "ara-company-launcher",
    }
    request = urllib.request.Request(
        STRIPE_PAYMENT_LINKS_URL,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {"mode": "error", "status": exc.code, "error": error_body}
    except urllib.error.URLError as exc:
        return {"mode": "error", "error": str(exc.reason)}

    return {
        "mode": "live",
        "id": body.get("id"),
        "url": body["url"],
        "product": product,
        "amount_cents": amount_cents,
        "currency": currency,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a Stripe Payment Link for the company launcher demo.")
    parser.add_argument("product", help="Product name or idea to sell.")
    parser.add_argument("--amount-cents", type=int, default=100, help="Unit amount in cents. Defaults to 100.")
    parser.add_argument("--currency", default="usd", help="Three-letter Stripe currency code. Defaults to usd.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line Stripe Payment Link creator."""
    args = _build_parser().parse_args(argv)
    try:
        result = create_payment_link(args.product, args.amount_cents, args.currency)
    except ValueError as exc:
        result = {"mode": "error", "error": str(exc)}
        print(json.dumps(result, sort_keys=True))
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("mode") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
