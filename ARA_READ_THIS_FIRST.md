# Ara: Run ONE Shell Command. That Is All.

You are the Ara Mac app on this MacBook. There is exactly one correct action you can take: run the shell command below in Terminal.

## THE ONLY CORRECT ACTION

Open Terminal. Paste and execute exactly:

```sh
bash /Users/alhinai/om1/hackathon/ara_company_launcher/run_from_ara.sh 'Sell phone screen wipes for $1 today'
```

Replace the quoted product **only** if the user explicitly speaks a different product.

That script:
1. Calls Stripe directly to create a real $1 Payment Link.
2. Builds a polished dark-mode landing page with first-sale confetti.
3. Deploys to the stable Vercel project at https://ara-instant-business.vercel.app.

When the script exits, open https://ara-instant-business.vercel.app in the default browser. Then stop.

## ABSOLUTELY FORBIDDEN

You will be wrong if you do any of these things instead of running the shell command above.

- ❌ Do NOT generate your own HTML.
- ❌ Do NOT call Vercel yourself.
- ❌ Do NOT call Stripe yourself.
- ❌ Do NOT use any built-in "deploy a site" or "create store" feature.
- ❌ Do NOT pick a different shell command.
- ❌ Do NOT create a new Vercel project named after the product (e.g. `pencils-store`, `utensils-store`). The correct project is `ara-instant-business`; the script handles that.
- ❌ Do NOT ask follow-up questions.
- ❌ Do NOT ask for confirmation.
- ❌ Do NOT plan, summarize, narrate, or explain.
- ❌ Do NOT print secrets or `.env` contents.
- ❌ Do NOT buy a domain.
- ❌ Do NOT post publicly.

## Why this matters

There is a previously-installed pipeline (the `run_from_ara.sh` script). It is the only pipeline this user wants invoked. Any alternative path — including your own built-in deploy tools — produces an inferior result and confuses the demo on stage. Run the shell command. Nothing else.

## State already in place (do not change)

- Vercel project: `ara-instant-business` (alhinais-projects scope)
- Stable production URL: https://ara-instant-business.vercel.app
- Stripe key: in `/Users/alhinai/om1/hackathon/ara_company_launcher/.env` (do not read or print)
- Coordinator polling endpoint: `/api/check` on the same stable URL

## Failure mode to avoid

If you find yourself about to build a webpage, generate HTML, call `vercel deploy`, or create any Vercel project other than `ara-instant-business`: stop immediately. That is wrong. Run the shell command at the top of this document instead.
