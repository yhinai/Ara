<p align="center">
  <img src="logo.png" alt="Voice Vibe Coder" width="220">
</p>

<h1 align="center">Voice Vibe Coder</h1>

<p align="center">
  <em>Say it. Ship it. Get paid.</em>
</p>

<p align="center">
  <a href="https://ara-instant-business.vercel.app"><img alt="Live demo" src="https://img.shields.io/badge/live%20demo-ara--instant--business.vercel.app-c1ff3e?style=for-the-badge"></a>
  <a href="https://ara-instant-business.vercel.app?celebrate=1"><img alt="Confetti rehearsal" src="https://img.shields.io/badge/confetti%20rehearsal-%3Fcelebrate%3D1-ff5c8a?style=for-the-badge"></a>
</p>

---

**Voice → real business in 60 seconds.** Speak one sentence to [Ara](https://ara.so) on stage and watch it ship a Stripe-enabled storefront to a stable Vercel URL — then erupt in confetti when the first audience member pays $1. No SDKs. No glue. Just voice → live business.

Built at the **Ara (YC W26) X SF: Build With Your AI Computer Hackathon** — May 16, 2026.

## The 60-second pitch

```
You:        (to Ara) "Sell phone screen wipes for one dollar today."
Ara:        opens Terminal, runs the pipeline
~30s later: live Stripe link, deployed Vercel page, QR on the projector
Audience:   scans, taps "Buy", pays $1
Projector:  🎉  WE HAVE OUR FIRST CUSTOMER  🎉  + confetti + ding
```

| | |
|---|---|
| **Live demo** | https://ara-instant-business.vercel.app |
| **Confetti rehearsal** (no real sale needed) | https://ara-instant-business.vercel.app?celebrate=1 |
| **Submitted to** | https://ara-sf-hack.mentormates.ai/projects |

## The one voice command

Tell Ara, verbatim:

> *"Open Terminal and run exactly: `cd /Users/alhinai/om1 && bash hackathon/ara_company_launcher/run_from_ara.sh 'Sell phone screen wipes for one dollar today'` — do not ask follow-up questions."*

The script auto-falls back to a hardcoded idea if Ara mishears, and the deploy goes to the same stable production URL every time — so you can pre-print the QR code.

## What it does (no-SDK pipeline)

```
voice ── Ara ── Terminal ── run_from_ara.sh ── launch_company.py
                                                    │
                                  ┌─────────────────┼─────────────────┐
                                  ▼                 ▼                 ▼
                            Stripe API        site_builder.py    Vercel deploy
                          (payment link)    (dark-mode HTML)   (stable prod URL)
                                  │                 │                 │
                                  └─────────────────┼─────────────────┘
                                                    ▼
                                       https://ara-instant-business.vercel.app
                                                    │
                                                    ▼
                                  audience scans QR ──► Stripe Checkout ──► $1 charge
                                                    │
                              ◄─── coordinator /api/check polls Stripe ───┐
                                                    │                     │
                                              confetti fires              │
                                                    └─ first sale detected ┘
```

- **Python stdlib only** — `urllib` calls Stripe directly. No `stripe` SDK, no `requests`, no `npm` for the runtime.
- **Single-file site template** — `site_builder.py` renders a premium dark-mode landing page with gradient text, glass cards, lime CTA, and an inline `<script>` confetti hook.
- **Stable Vercel project** — every deploy goes to `ara-instant-business` so the QR code never changes.
- **`/api/check` coordinator** — Python serverless function polls Stripe Checkout Sessions for paid `payment_link` matches; landing page fetches every 2s for first-sale confetti.
- **Rehearsal hook** — `?celebrate=1` previews the wow moment for projector testing without a real sale.

## Repo layout

```
hackathon/ara_company_launcher/
├── run_from_ara.sh           # entry point invoked by Ara
├── launch_company.py         # orchestrator: idea → Stripe → site → Vercel
├── site_builder.py           # premium dark landing page generator
├── stripe_link.py            # urllib-based Stripe Payment Links API client
├── site_template_api/
│   └── check.py              # /api/check coordinator polling Stripe
├── vercel_link/
│   └── project.json          # stable Vercel project binding
├── DEMO_CARD.md              # on-stage cheat sheet
├── demo_runbook.md           # full setup + hour-by-hour plan
└── ARA_READ_THIS_FIRST.md    # Ara-facing onboarding
```

## Run it yourself

Verified Ara Mac app:

- `/Applications/Ara.app` · bundle `com.ara.app` · v0.1.92 build 439

```sh
# clone
gh repo clone yhinai/Ara && cd Ara

# configure Stripe + Vercel + scope (see .env.example)
cp .env.example .env  &&  $EDITOR .env

# one-shot launch
bash run_from_ara.sh "Sell custom dog bandanas for \$1 today"
```

Open the printed Vercel URL or your stable production URL. Confetti fires on the first `payment_status: paid` Stripe Checkout Session.

## Live switches (in `.env`)

```sh
STRIPE_SECRET_KEY=sk_live_...      # use sk_live_ for real audience charges
COMPANY_LAUNCH_LIVE_STRIPE=1       # 0 = dry-run with placeholder link
COMPANY_LAUNCH_DEPLOY=1            # 0 = local-only, skip vercel
COMPANY_LAUNCH_PROD=1              # 1 = always update stable prod URL
COMPANY_LAUNCH_VERCEL_SCOPE=...    # vercel team slug
COMPANY_LAUNCH_POST=0              # 1 = post share copy to webhook
```

Public posting (`COMPANY_LAUNCH_POST=1`) requires `COMPANY_LAUNCH_POST_WEBHOOK_URL` — intentionally guarded.

## Credits

- Built on [Ara](https://ara.so) (YC W26).
- Hosted by [MentorMates](https://ara-sf-hack.mentormates.ai/) at the European Startup Embassy, SF.
- Powered by Stripe Payment Links + Vercel serverless + Python stdlib.

---

<p align="center"><em>Speak. Ship. Get paid. — Voice Vibe Coder</em></p>
