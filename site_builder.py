from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_PAYMENT_URL = "https://buy.stripe.com/test_demo_link"

_TRAILING_STOPWORDS = {
    "at", "in", "for", "of", "with", "by", "to", "from", "on",
    "and", "or", "but", "the", "a", "an",
}

_SPELLED_NUMBER_WORDS = (
    "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    "thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    "twenty|thirty|forty|fifty|hundred"
)


def _strip_price_phrases(text: str) -> str:
    """Remove '$3', '3 dollars', 'ten bucks', '5 USD' so they don't leak into the brand."""
    text = re.sub(r"\$\d+(?:\.\d{1,2})?", "", text)
    text = re.sub(r"\b\d+(?:\.\d{1,2})?\s*(?:dollars?|bucks?|usd)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b(?:{_SPELLED_NUMBER_WORDS})\b\s*(?:dollars?|bucks?|usd)?\b", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip(" .,")

_EMOJI_LOOKUP = [
    (("dog", "puppy", "cat", "pet", "bandana", "collar", "leash"), "🐾"),
    (("coffee", "espresso", "latte", "cappuccino", "brew", "cafe"), "☕"),
    (("tea", "matcha", "boba"), "🍵"),
    (("taco", "burrito", "salsa", "queso"), "🌮"),
    (("pizza",), "🍕"),
    (("burger",), "🍔"),
    (("sushi",), "🍣"),
    (("donut", "doughnut"), "🍩"),
    (("cookie", "cookies"), "🍪"),
    (("cake", "cupcake", "bake", "bakery"), "🧁"),
    (("ice", "icecream"), "🍦"),
    (("juice", "smoothie", "lemonade"), "🥤"),
    (("beer", "brewery"), "🍺"),
    (("wine",), "🍷"),
    (("plant", "garden", "flower", "bouquet"), "🌱"),
    (("book", "zine", "magazine"), "📚"),
    (("art", "painting", "print", "poster", "sticker"), "🎨"),
    (("music", "vinyl", "record", "song"), "🎵"),
    (("game", "arcade"), "🎮"),
    (("photo", "camera", "polaroid"), "📷"),
    (("shirt", "tshirt", "tee", "hoodie", "merch", "apparel"), "👕"),
    (("hat", "cap"), "🧢"),
    (("shoe", "sneaker"), "👟"),
    (("candle", "soap", "scent"), "🕯"),
    (("soap",), "🧼"),
    (("crypto", "bitcoin", "eth", "nft"), "🪙"),
    (("ai", "robot", "bot"), "🤖"),
    (("rocket", "launch", "startup"), "🚀"),
]


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:54].strip("-") or "instant-company"


def _title_from_idea(idea: str, city: str = "") -> str:
    cleaned = _strip_price_phrases(idea)
    cleaned = re.sub(r"\s+", " ", cleaned.strip().rstrip("."))
    cleaned = re.sub(r"^(sell|build|launch|make|start|create)\s+", "", cleaned, flags=re.IGNORECASE)
    if city.strip():
        cleaned = re.sub(rf"\s+in\s+{re.escape(city.strip())}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+for\s+(?:today)?\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+today\b", "", cleaned, flags=re.IGNORECASE)
    words = re.findall(r"[A-Za-z0-9]+", cleaned.title())[:4]
    while len(words) > 1 and words[-1].lower() in _TRAILING_STOPWORDS:
        words.pop()
    if not words or (len(words) == 1 and words[0].lower() in _TRAILING_STOPWORDS):
        return "Instant Company"
    return " ".join(words)


def _price_label(amount_cents: int) -> str:
    dollars = amount_cents / 100
    return f"${int(dollars)}" if dollars.is_integer() else f"${dollars:.2f}"


def _hero_emoji(brand: str, idea: str) -> str:
    haystack = f"{brand} {idea}".lower()
    tokens = set(re.findall(r"[a-z]+", haystack))
    for keywords, emoji in _EMOJI_LOOKUP:
        if any(kw in tokens for kw in keywords):
            return emoji
    return "🚀"


def _tagline(brand: str, idea: str) -> str:
    cleaned = _strip_price_phrases(idea)
    cleaned = re.sub(r"\s+", " ", cleaned.strip().rstrip("."))
    cleaned = re.sub(r"^(sell|build|launch|make|start|create)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+today\b", "", cleaned, flags=re.IGNORECASE).strip(" .,")
    words = cleaned.split()
    if 7 <= len(words) <= 12:
        return cleaned[0].upper() + cleaned[1:]
    short = " ".join(words[:8]) if words else brand.lower()
    return f"A first drop of {short}, reserved before the demo ends."


def _feature_cards(brand: str, idea: str) -> list[tuple[str, str, str]]:
    haystack = f"{brand} {idea}".lower()
    tokens = set(re.findall(r"[a-z]+", haystack))

    def has(*kws: str) -> bool:
        return any(k in tokens for k in kws)

    if has("coffee", "espresso", "latte", "cafe", "brew"):
        return [
            ("☕", "Single-origin beans", "Roasted this week, ground to order."),
            ("🥛", "Oat or whole milk", "Pick your pour at pickup."),
            ("⚡", "Ready in 3 minutes", "Skip the line, grab and go."),
        ]
    if has("dog", "cat", "pet", "bandana", "collar"):
        return [
            ("🧵", "Hand-sewn locally", "Stitched in small batches."),
            ("🌿", "Pre-shrunk cotton", "Soft on fur, machine washable."),
            ("📦", "Ships next day", "Tracked from our door to yours."),
        ]
    if has("taco", "burrito", "pizza", "burger", "sushi", "food"):
        return [
            ("🔥", "Made to order", "Cooked when you tap pay."),
            ("🌱", "Sourced locally", "From farms within 50 miles."),
            ("⏱", "Ready in 8 minutes", "Grab it on your way through."),
        ]
    if has("candle", "soap", "scent", "fragrance"):
        return [
            ("🕯", "Hand-poured", "Made in tiny batches each week."),
            ("🌿", "Clean ingredients", "Soy wax, real essential oils."),
            ("📦", "Ships in 48 hours", "Wrapped and on its way."),
        ]
    if has("shirt", "tshirt", "tee", "hoodie", "merch", "apparel"):
        return [
            ("👕", "Heavyweight cotton", "Built to soften with every wash."),
            ("🎨", "Printed in-house", "Each piece inspected by hand."),
            ("📦", "Ships next day", "Tracked shipping included."),
        ]
    if has("art", "print", "poster", "sticker", "zine"):
        return [
            ("🎨", "Original artwork", "Designed for this drop only."),
            ("📐", "Archival paper", "Built to last on your wall."),
            ("📦", "Ships flat", "Protected, tracked, signed."),
        ]
    if has("ai", "bot", "saas", "software", "app"):
        return [
            ("⚡", "Instant access", "Live the moment you check out."),
            ("🔒", "Private by default", "Your data stays your data."),
            ("🛠", "Built today", "Ship-grade from minute one."),
        ]
    return [
        ("✨", "Limited first drop", "Only a handful for this demo."),
        ("⚡", "Reserved instantly", "Tap pay and your spot is yours."),
        ("🤝", "Built for the room", "First customers shape the next one."),
    ]


def _render_index(
    idea: str,
    city: str,
    payment_url: str,
    amount_cents: int,
    payment_link_id: str = "",
    coordinator_url: str = "",
) -> tuple[str, dict[str, str]]:
    brand = _title_from_idea(idea, city)
    price = _price_label(amount_cents)
    hero_emoji = _hero_emoji(brand, idea)
    tagline = _tagline(brand, idea)
    cards = _feature_cards(brand, idea)

    headline = f"{brand} is live"
    if city.strip():
        headline = f"{brand} is live in {city.strip()}"

    esc_brand = html.escape(brand)
    esc_brand_upper = html.escape(brand.upper())
    esc_headline = html.escape(headline)
    esc_tagline = html.escape(tagline)
    esc_payment_url = html.escape(payment_url, quote=True)
    esc_price = html.escape(price)
    esc_emoji = html.escape(hero_emoji)
    esc_plink_id = html.escape(payment_link_id, quote=True)
    esc_coord_url = html.escape(coordinator_url, quote=True)
    esc_description = html.escape(headline, quote=True)

    cards_html = "\n".join(
        f"""        <div class="feature-card">
          <div class="feature-emoji">{html.escape(emoji)}</div>
          <div class="feature-title">{html.escape(title)}</div>
          <div class="feature-desc">{html.escape(desc)}</div>
        </div>"""
        for emoji, title, desc in cards
    )

    metadata = {
        "brand": brand,
        "slug": _slug(brand),
        "headline": headline,
    }

    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc_description}">
  <meta name="x-payment-link-id" content="{esc_plink_id}">
  <meta name="x-coordinator-url" content="{esc_coord_url}">
  <title>{esc_brand}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      background: #0a0a0a;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}
    body {{
      min-height: 100vh;
      background: radial-gradient(ellipse at top, #1a1a2e 0%, #0a0a0a 100%);
      overflow-x: hidden;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      height: 80px;
      width: 100%;
      z-index: 50;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      background: rgba(0, 0, 0, 0.5);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 clamp(20px, 4vw, 48px);
    }}
    .wordmark {{
      font-size: 12px;
      letter-spacing: 4px;
      text-transform: uppercase;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.85);
    }}
    .live-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.8);
    }}
    .live-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 10px rgba(34, 197, 94, 0.8);
      animation: pulse 1.6s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.5; transform: scale(0.85); }}
    }}
    .hero {{
      position: relative;
      min-height: calc(100vh - 80px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: clamp(40px, 8vw, 96px) clamp(20px, 5vw, 48px);
      overflow: hidden;
    }}
    .hero-blob {{
      position: absolute;
      top: -10%;
      left: 50%;
      transform: translateX(-50%);
      width: 800px;
      height: 800px;
      background: conic-gradient(from 180deg at 50% 50%, rgba(193, 255, 62, 0.18), rgba(120, 80, 255, 0.16), rgba(255, 100, 180, 0.12), rgba(193, 255, 62, 0.18));
      filter: blur(120px);
      opacity: 0.6;
      pointer-events: none;
      z-index: 0;
    }}
    .hero-inner {{
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 24px;
      max-width: 880px;
    }}
    .hero-emoji {{
      font-size: 96px;
      line-height: 1;
      filter: drop-shadow(0 12px 40px rgba(0, 0, 0, 0.6));
    }}
    .hero-wordmark {{
      font-size: 12px;
      letter-spacing: 4px;
      text-transform: uppercase;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.6);
    }}
    h1 {{
      font-size: clamp(48px, 7vw, 96px);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.02;
      background: linear-gradient(180deg, #ffffff 0%, #9ca3af 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .subhead {{
      font-size: 22px;
      opacity: 0.75;
      max-width: 640px;
      line-height: 1.45;
      color: #ffffff;
    }}
    .cta-block {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      margin-top: 8px;
    }}
    .cta {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: #c1ff3e;
      color: #000;
      font-size: 22px;
      font-weight: 700;
      padding: 18px 48px;
      border-radius: 999px;
      text-decoration: none;
      box-shadow: 0 0 60px rgba(193, 255, 62, 0.3);
      transition: transform 0.18s ease, box-shadow 0.18s ease;
    }}
    .cta:hover {{
      transform: scale(1.04);
      box-shadow: 0 0 80px rgba(193, 255, 62, 0.45);
    }}
    .price-label {{
      font-size: 13px;
      opacity: 0.6;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    .features {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      width: 100%;
      max-width: 1080px;
      margin: 80px auto 0;
      padding: 0 clamp(20px, 5vw, 48px) 80px;
      position: relative;
      z-index: 1;
    }}
    .feature-card {{
      padding: 32px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 20px;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
    }}
    .feature-emoji {{
      font-size: 32px;
      margin-bottom: 16px;
      line-height: 1;
    }}
    .feature-title {{
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #ffffff;
    }}
    .feature-desc {{
      font-size: 15px;
      line-height: 1.5;
      color: rgba(255, 255, 255, 0.6);
    }}
    .footer {{
      padding: 32px;
      text-align: center;
      font-size: 12px;
      opacity: 0.4;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    @media (max-width: 720px) {{
      .features {{ grid-template-columns: 1fr; }}
      .hero-emoji {{ font-size: 80px; }}
      .subhead {{ font-size: 18px; }}
      .cta {{ font-size: 18px; padding: 16px 36px; }}
    }}
    .celebrate-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(5, 5, 10, 0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 24px;
      z-index: 9999;
      opacity: 0;
      transition: opacity 300ms ease;
      pointer-events: none;
    }}
    .celebrate-overlay.show {{
      opacity: 1;
      pointer-events: auto;
    }}
    .celebrate-emoji {{
      font-size: 120px;
      line-height: 1;
      animation: bounce 0.9s ease-in-out infinite;
    }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-24px); }}
    }}
    .celebrate-headline {{
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.02em;
      text-align: center;
      padding: 0 24px;
      background: linear-gradient(90deg, #ffffff 0%, #c1ff3e 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .celebrate-brand {{
      font-size: 14px;
      letter-spacing: 4px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.7);
    }}
    .confetti-piece {{
      position: fixed;
      top: -20px;
      width: 10px;
      height: 14px;
      z-index: 9998;
      pointer-events: none;
      border-radius: 2px;
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="wordmark">{esc_brand_upper}</div>
    <div class="live-pill"><span class="live-dot"></span>Live</div>
  </header>
  <section class="hero">
    <div class="hero-blob"></div>
    <div class="hero-inner">
      <div class="hero-emoji">{esc_emoji}</div>
      <div class="hero-wordmark">{esc_brand_upper}</div>
      <h1>{esc_headline}</h1>
      <p class="subhead">{esc_tagline}</p>
      <div class="cta-block">
        <a class="cta" href="{esc_payment_url}">Reserve for {esc_price}</a>
        <div class="price-label">{esc_price} - first customer offer</div>
      </div>
    </div>
  </section>
  <section class="features">
{cards_html}
  </section>
  <footer class="footer">{esc_brand} - Powered by Ara - Launched seconds ago</footer>

  <div class="celebrate-overlay" id="celebrate">
    <div class="celebrate-emoji">🎉</div>
    <div class="celebrate-headline">WE HAVE OUR FIRST CUSTOMER</div>
    <div class="celebrate-brand">{esc_brand_upper}</div>
  </div>

  <script>
    (function () {{
      const launchTs = Date.now();
      const POLL_MS = 2000;
      const MAX_RUN_MS = 30 * 60 * 1000;
      const plinkId = document.querySelector('meta[name="x-payment-link-id"]').getAttribute('content') || '';
      const coordinatorUrl = document.querySelector('meta[name="x-coordinator-url"]').getAttribute('content') || '';
      let lastCount = 0;
      let fired = false;

      function makeConfetti() {{
        for (let i = 0; i < 150; i++) {{
          const piece = document.createElement('div');
          piece.className = 'confetti-piece';
          const hue = Math.floor(Math.random() * 360);
          piece.style.background = 'hsl(' + hue + ', 90%, 60%)';
          piece.style.left = (Math.random() * 100) + 'vw';
          document.body.appendChild(piece);
          const driftX = (Math.random() - 0.5) * 300;
          const rotate = (Math.random() * 720 - 360);
          const duration = 2000 + Math.random() * 2000;
          const anim = piece.animate(
            [
              {{ transform: 'translate(0, 0) rotate(0deg)', opacity: 1 }},
              {{ transform: 'translate(' + driftX + 'px, 110vh) rotate(' + rotate + 'deg)', opacity: 0.9 }}
            ],
            {{ duration: duration, easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)' }}
          );
          anim.onfinish = function () {{ piece.remove(); }};
        }}
      }}

      function playDing() {{
        try {{
          const Ctx = window.AudioContext || window.webkitAudioContext;
          if (!Ctx) return;
          const ctx = new Ctx();
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = 880;
          gain.gain.setValueAtTime(0.3, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
          osc.connect(gain).connect(ctx.destination);
          osc.start();
          osc.stop(ctx.currentTime + 0.55);
        }} catch (e) {{ /* silent */ }}
      }}

      function celebrate() {{
        if (fired) return;
        fired = true;
        const overlay = document.getElementById('celebrate');
        overlay.classList.add('show');
        playDing();
        makeConfetti();
        setTimeout(function () {{ overlay.classList.remove('show'); }}, 6000);
      }}

      function poll() {{
        if (fired) return;
        if (Date.now() - launchTs > MAX_RUN_MS) return;
        const since = Math.floor(launchTs / 1000);
        const url = coordinatorUrl + (coordinatorUrl.indexOf('?') >= 0 ? '&' : '?')
          + 'link_id=' + encodeURIComponent(plinkId)
          + '&since=' + since;
        fetch(url, {{ cache: 'no-store' }})
          .then(function (r) {{ return r.ok ? r.json() : null; }})
          .then(function (data) {{
            if (!data) return;
            const count = Number(data.count || 0);
            if (lastCount === 0 && count >= 1) {{
              celebrate();
            }}
            lastCount = count;
          }})
          .catch(function () {{ /* silent retry */ }})
          .finally(function () {{
            if (!fired) setTimeout(poll, POLL_MS);
          }});
      }}

      if (coordinatorUrl) {{
        setTimeout(poll, POLL_MS);
      }}

      // Dev hook: trigger ?celebrate=1 in URL fires the moment manually.
      if (location.search.indexOf('celebrate=1') >= 0) {{
        setTimeout(celebrate, 400);
      }}
    }})();
  </script>
</body>
</html>
"""
    return index, metadata


def build_landing_page(
    idea: str,
    city: str,
    payment_url: str,
    output_dir: str | Path,
    amount_cents: int = 100,
    payment_link_id: str = "",
    coordinator_url: str = "",
) -> dict[str, Any]:
    """Generate a static landing page and Vercel config using only the Python standard library."""
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    index, page_metadata = _render_index(
        idea=idea,
        city=city,
        payment_url=payment_url,
        amount_cents=amount_cents,
        payment_link_id=payment_link_id,
        coordinator_url=coordinator_url,
    )
    vercel_config = {
        "cleanUrls": True,
        "trailingSlash": False,
        "headers": [
            {
                "source": "/(.*)",
                "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}],
            }
        ],
    }

    index_path = target_dir / "index.html"
    vercel_path = target_dir / "vercel.json"
    index_path.write_text(index, encoding="utf-8")
    vercel_path.write_text(json.dumps(vercel_config, indent=2) + "\n", encoding="utf-8")

    return {
        "brand": page_metadata["brand"],
        "slug": page_metadata["slug"],
        "headline": page_metadata["headline"],
        "idea": idea,
        "city": city,
        "payment_url": payment_url,
        "amount_cents": amount_cents,
        "price_label": _price_label(amount_cents),
        "output_dir": str(target_dir),
        "payment_link_id": payment_link_id,
        "coordinator_url": coordinator_url,
        "files": {
            "index": str(index_path),
            "vercel": str(vercel_path),
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a no-SDK static landing page for the hackathon demo.")
    parser.add_argument("--idea", required=True, help="Business idea, e.g. 'Sell custom dog bandanas'.")
    parser.add_argument("--city", default="", help="Optional launch city shown on the page.")
    parser.add_argument("--payment-url", default=DEFAULT_PAYMENT_URL, help="Stripe Payment Link or dry-run URL.")
    parser.add_argument("--amount-cents", type=int, default=100, help="Price in cents. Defaults to 100.")
    parser.add_argument("--output-dir", required=True, help="Directory where index.html and vercel.json are written.")
    parser.add_argument("--payment-link-id", default="", help="Stripe payment link id for confetti polling.")
    parser.add_argument("--coordinator-url", default="", help="Coordinator endpoint URL polled for first-sale signal.")
    return parser


def main() -> int:
    """Run the command-line site builder."""
    args = _parser().parse_args()
    metadata = build_landing_page(
        idea=args.idea,
        city=args.city,
        payment_url=args.payment_url,
        output_dir=args.output_dir,
        amount_cents=args.amount_cents,
        payment_link_id=args.payment_link_id,
        coordinator_url=args.coordinator_url,
    )
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
