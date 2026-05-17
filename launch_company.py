from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

from site_builder import build_landing_page
from stripe_link import create_payment_link


ROOT = Path(__file__).resolve().parent
DEFAULT_BUILD_ROOT = ROOT / "build"
VERCEL_LINK_PROJECT_JSON = ROOT / "vercel_link" / "project.json"
API_TEMPLATE_DIR = ROOT / "site_template_api"
STABLE_PUBLIC_URL = "https://ara-instant-business.vercel.app"
DEFAULT_COORDINATOR_URL = f"{STABLE_PUBLIC_URL}/api/check"


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:54].strip("-") or "instant-company"


_SPELLED_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "twenty five": 25, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100,
}


def _amount_cents_from_idea(idea: str, fallback_cents: int) -> int:
    # "$3" or "$3.50"
    match = re.search(r"\$(\d+(?:\.\d{1,2})?)", idea)
    if match:
        return max(50, int(round(float(match.group(1)) * 100)))
    # "3 dollars" / "3 bucks" / "3 usd"
    match = re.search(r"(\d+(?:\.\d{1,2})?)\s*(?:dollars?|bucks?|usd)", idea, re.IGNORECASE)
    if match:
        return max(50, int(round(float(match.group(1)) * 100)))
    # spelled-out: "ten dollars", "twenty bucks" (longest match first)
    for word, n in sorted(_SPELLED_NUMBERS.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(word)}\b\s*(?:dollars?|bucks?|usd)?", idea, re.IGNORECASE):
            return n * 100
    return fallback_cents


def _product_from_idea(idea: str, city: str) -> str:
    product = re.sub(r"\s+", " ", idea.strip().rstrip("."))
    product = re.sub(r"^(sell|build|launch|make|start|create)\s+", "", product, flags=re.IGNORECASE)
    # Remove price phrases more aggressively
    product = re.sub(r"\$?\d+(?:\.\d{2})?\s*(?:dollars?|bucks?|usd)?", "", product, flags=re.IGNORECASE)
    if city.strip():
        product = re.sub(rf"\s+in\s+{re.escape(city.strip())}\b", "", product, flags=re.IGNORECASE)
    product = re.sub(r"\s+for\s+(?:today)?\b", "", product, flags=re.IGNORECASE)
    product = re.sub(r"\s+today\b", "", product, flags=re.IGNORECASE)
    product = re.sub(r"\s+", " ", product).strip()
    return product or idea.strip() or "instant product"


def _pin_to_fixed_project(site_dir: str) -> str | None:
    """Copy stable .vercel/project.json into site_dir so deploys land on the same project."""
    if not VERCEL_LINK_PROJECT_JSON.exists():
        return f"missing fixed project link at {VERCEL_LINK_PROJECT_JSON}"
    target = Path(site_dir) / ".vercel" / "project.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(VERCEL_LINK_PROJECT_JSON, target)
    return None


def _copy_api_endpoints(site_dir: str) -> None:
    """Copy serverless function templates into <site_dir>/api/ so they ship with the deploy."""
    if not API_TEMPLATE_DIR.is_dir():
        return
    api_target = Path(site_dir) / "api"
    api_target.mkdir(parents=True, exist_ok=True)
    for src in API_TEMPLATE_DIR.iterdir():
        if src.is_file() and not src.name.startswith("."):
            shutil.copyfile(src, api_target / src.name)


def deploy_to_vercel(site_dir: str) -> dict[str, Any]:
    """Deploy a static site directory to Vercel when explicitly enabled."""
    if os.getenv("COMPANY_LAUNCH_DEPLOY") != "1":
        return {
            "mode": "dry_run",
            "url": "",
            "note": "Set COMPANY_LAUNCH_DEPLOY=1 to run `vercel deploy`.",
        }
    if shutil.which("vercel") is None:
        return {"mode": "error", "error": "vercel CLI is not installed or not on PATH."}

    link_error = _pin_to_fixed_project(site_dir)
    if link_error:
        return {"mode": "error", "error": link_error}
    _copy_api_endpoints(site_dir)

    command = ["vercel", "deploy", "--yes", site_dir]
    if os.getenv("COMPANY_LAUNCH_PROD") == "1":
        command.insert(2, "--prod")
    if scope := os.getenv("COMPANY_LAUNCH_VERCEL_SCOPE"):
        command.extend(["--scope", scope])

    completed = subprocess.run(command, check=False, text=True, capture_output=True, timeout=180)
    if completed.returncode != 0:
        return {
            "mode": "error",
            "returncode": completed.returncode,
            "stderr": completed.stderr[-2000:],
        }

    output = completed.stdout.strip()
    url = ""
    if output.startswith("{"):
        try:
            body = json.loads(output)
            url = body.get("deployment", {}).get("url", "")
        except json.JSONDecodeError:
            url = ""
    if not url and output:
        url = output.splitlines()[-1]
    # Prefer the stable production domain when deploying to prod so QR codes never change.
    if os.getenv("COMPANY_LAUNCH_PROD") == "1":
        url = STABLE_PUBLIC_URL
    return {"mode": "live", "url": url, "stdout": completed.stdout[-2000:]}


def _price_label(amount_cents: int) -> str:
    dollars = amount_cents / 100
    return f"${int(dollars)}" if dollars.is_integer() else f"${dollars:.2f}"


def build_share_copy(brand: str, idea: str, public_url: str, payment_url: str, amount_cents: int) -> str:
    """Build guarded launch copy for manual sharing."""
    launch_url = public_url or payment_url
    return (
        f"Built live at the Ara SF hackathon from one prompt: {brand}.\n\n"
        f"Idea: {idea}\n"
        f"First {_price_label(amount_cents)} preorder: {launch_url}\n\n"
        "This is a guarded demo: real checkout path, no public spam."
    )


def post_to_webhook(message: str) -> dict[str, Any]:
    """Post only when a private webhook and explicit live-post flag are configured."""
    webhook_url = os.getenv("COMPANY_LAUNCH_POST_WEBHOOK_URL")
    if os.getenv("COMPANY_LAUNCH_POST") != "1" or not webhook_url:
        return {
            "mode": "dry_run",
            "note": "Posting skipped. Set COMPANY_LAUNCH_POST=1 and COMPANY_LAUNCH_POST_WEBHOOK_URL to post.",
        }

    request = urllib.request.Request(
        webhook_url,
        data=json.dumps({"text": message}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return {"mode": "live", "status": response.status}


def launch_company(idea: str, city: str, amount_cents: int, output_dir: str | None = None) -> dict[str, Any]:
    """Run the complete no-SDK company launch flow."""
    amount_cents = _amount_cents_from_idea(idea, amount_cents)
    product = _product_from_idea(idea, city)
    payment = create_payment_link(product=product, amount_cents=amount_cents, currency="usd")
    payment_url = payment.get("url", "")

    if output_dir is None:
        output_dir = str(DEFAULT_BUILD_ROOT / f"{int(time.time())}-{_slug(product)}")

    site = build_landing_page(
        idea=idea,
        city=city,
        payment_url=payment_url,
        output_dir=output_dir,
        amount_cents=amount_cents,
        payment_link_id=payment.get("id", ""),
        coordinator_url=os.getenv("COMPANY_LAUNCH_COORDINATOR_URL", DEFAULT_COORDINATOR_URL),
    )
    deployment = deploy_to_vercel(site["output_dir"])
    public_url = deployment.get("url") or ""
    share_copy = build_share_copy(
        brand=site["brand"],
        idea=idea,
        public_url=public_url,
        payment_url=payment_url,
        amount_cents=amount_cents,
    )
    posting = post_to_webhook(share_copy)

    return {
        "idea": idea,
        "city": city,
        "product": product,
        "amount_cents": amount_cents,
        "price_label": _price_label(amount_cents),
        "payment": payment,
        "site": site,
        "deployment": deployment,
        "share_copy": share_copy,
        "posting": posting,
        "next_live_steps": [
            "Open the generated site or Vercel URL.",
            "Click the $1 button and stop at Stripe Checkout unless using approved test payment details.",
            "Paste share_copy manually only into an approved private destination.",
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="No-SDK Ara hackathon company launcher.")
    parser.add_argument("idea", help="One-sentence launch idea.")
    parser.add_argument("--city", default="", help="Optional launch city shown on the page.")
    parser.add_argument("--amount-cents", type=int, default=500, help="Stripe amount in cents. Defaults to $5.")
    parser.add_argument("--output-dir", help="Optional static site output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line launcher."""
    args = _parser().parse_args(argv)
    result = launch_company(
        idea=args.idea,
        city=args.city,
        amount_cents=args.amount_cents,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["payment"].get("mode") != "error" and result["deployment"].get("mode") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
