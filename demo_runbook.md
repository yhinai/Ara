# Ara Company Launcher Demo Runbook

5-minute hackathon demo plan for the no-SDK pivot. The story: one voice prompt in the installed Ara Mac app becomes a paid micro-business launch with Stripe, Vercel, and guarded share copy.

Local app verified:

- `/Applications/Ara.app`
- Bundle id: `com.ara.app`
- Version `0.1.92` build `439`

## Setup Env Vars

Use test-mode keys unless the team has explicitly approved live credentials.

```sh
export STRIPE_SECRET_KEY="sk_test_..."
export COMPANY_LAUNCH_LIVE_STRIPE=1
export COMPANY_LAUNCH_DEPLOY=1
export COMPANY_LAUNCH_PROD=0
export COMPANY_LAUNCH_POST_WEBHOOK_URL=""
```

Keep posting disabled for the judged demo unless the destination is private and pre-approved. If Stripe or Vercel credentials are missing, switch to the failure fallback below instead of improvising live.

## Voice Opener

Open the Ara Mac app, say this clearly, then pause:

> Launch a one-dollar storefront for custom dog bandanas in Brooklyn today.

Narrate the parser result as it appears: product, audience, price, page copy, payment link, deploy target, and proposed social post.

## Dry-Run Rehearsal

Before the room demo:

1. Run once with posting disabled and confirm the app completes without needing the Ara SDK.
2. Confirm the generated business idea, Stripe price/payment link, Vercel URL, and share copy are visible.
3. Open the landing page and click through to the Stripe checkout page, stopping before payment.
4. Keep the final successful URL, payment link, and screenshots available as backup tabs.

Time target: 60 seconds from voice prompt to deployed URL.

## Live Stripe/Vercel Flow

Narration beats:

1. "We are not using a private Ara SDK. This is a plain integration path: prompt in, Stripe out, static site deployed."
2. Trigger the launch from the prepared voice opener.
3. Show the Stripe Payment Link creation in test mode.
4. Show the generated landing page files or preview.
5. Deploy to Vercel and open the public URL.
6. Click the buy button and show the Stripe checkout screen.
7. Return to the generated share copy, but do not post publicly.

Keep the browser tabs preloaded in this order: demo app, Vercel dashboard or deployment output, deployed site, Stripe checkout, backup deployed site.

## Public Posting Guardrails

Do not auto-post to Reddit, X, Discord, Slack, or any public community during judging.

Allowed:

- Copy text into a private notes window.
- Post only to a private team channel if everyone has approved it.
- Say what would be posted and why the guardrail exists.

Blocked:

- Public posts from the judge room.
- Claims that inventory, fulfillment, or customer support exists.
- Using real customer data or production Stripe keys.

## Failure Fallback

If live Stripe fails:

- Use the saved test Payment Link backup.
- Say: "The live API call is rate-limited, so I am switching to the preflight test link from the same flow."

If Vercel deploy fails:

- Open the saved Vercel URL or local generated `index.html`.
- Say: "The deployment provider is slow, so I am showing the last successful build artifact and public URL."

If voice input fails:

- Paste the opener as text.
- Say: "Voice is only the input layer; the no-SDK launch flow is the part being judged."

If everything fails:

- Show the backup screenshots in order: prompt, Stripe link, generated page, deployed URL, checkout.
- Keep the narrative calm and focus on the integration path.

## Judge-Facing Narration

Opening:

> "We pivoted away from the nonexistent Ara SDK. This demo is deliberately no-SDK: it uses ordinary service APIs and deploy tooling to turn one sentence into a tiny paid launch."

Middle:

> "The important part is not a chatbot draft. It creates a price, gives the page a real checkout path, deploys the storefront, and prepares guarded distribution copy."

Guardrail:

> "We stop before public posting because hackathon demos should not spam communities or imply a real fulfillment operation."

Close:

> "In five minutes, the founder gets the first testable version of a business: offer, payment, page, URL, and launch copy, all without depending on a private SDK."
