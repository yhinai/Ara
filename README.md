# Ara Company Launcher

Hackathon demo: say one sentence, then Ara turns it into a real tiny business launch.

Target moment:

1. Parse the idea.
2. Create a $1 Stripe Payment Link.
3. Generate a landing page.
4. Deploy it to Vercel.
5. Produce share copy for the room chat or Reddit group.

Domain buying and public posting are intentionally guarded. Use the Vercel URL for the live demo unless you have already tested domain/provider credentials.

## One-Command No-SDK Demo

This is meant to be invoked from the installed Ara Mac app. Verified local app:

- `/Applications/Ara.app`
- Bundle id: `com.ara.app`
- Version: `0.1.92` build `439`

Ara prompt: [ara_app_prompt.md](ara_app_prompt.md)

Most reliable Ara voice command:

```text
Do not ask follow-up questions. Use Terminal and run exactly:
cd /Users/alhinai/om1 && bash hackathon/ara_company_launcher/run_from_ara.sh 'Sell baby Band-Aids for $1 today'
```

For live end-to-end mode, create `hackathon/ara_company_launcher/.env` from
`.env.example` and put your Stripe test secret there. The file is gitignored.

```sh
uv run python hackathon/ara_company_launcher/launch_company.py \
  'Sell custom dog bandanas for $1 today'
```

The command creates or dry-runs a Stripe Payment Link, writes a polished static `index.html`,
optionally deploys the site to Vercel, and prints JSON metadata/share copy for Ara to read back.
It uses only the Python standard library and does not import `ara_sdk`.

Good opener:

> Sell custom dog bandanas for $1 today.

## Local Dry Run

```sh
uv run python hackathon/ara_company_launcher/launch_company.py \
  'Sell custom dog bandanas for $1 today' \
  --output-dir /tmp/ara-company-launcher-demo
```

Open `/tmp/ara-company-launcher-demo/index.html` or deploy that directory with Vercel.

## Live Switches

```sh
export STRIPE_SECRET_KEY="sk_test_..."
export COMPANY_LAUNCH_LIVE_STRIPE=1
export COMPANY_LAUNCH_DEPLOY=1
export COMPANY_LAUNCH_PROD=0
```

Public posting stays off unless both `COMPANY_LAUNCH_POST=1` and
`COMPANY_LAUNCH_POST_WEBHOOK_URL` are set.

## Open Ara Ready To Launch

Use this helper instead of opening Ara directly:

```sh
bash hackathon/ara_company_launcher/bin/open_ara_ready.sh
```

It opens the installed Ara Mac app and copies the exact no-follow-up launch prompt to your clipboard. Paste it into Ara, or tell Ara: "Use the prompt I copied to the clipboard."
