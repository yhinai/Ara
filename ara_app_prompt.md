# Ara App Prompt

Use this inside the installed Ara Mac app, not an SDK.

Ara app verified locally:

- App path: `/Applications/Ara.app`
- Bundle id: `com.ara.app`
- Version: `0.1.92` build `439`

Paste or say this to Ara:

```text
You are running on my MacBook in the Ara desktop app.

Read this local instruction file first:
/Users/alhinai/om1/hackathon/ara_company_launcher/ARA_READ_THIS_FIRST.md

cd /Users/alhinai/om1 && bash hackathon/ara_company_launcher/run_from_ara.sh 'Sell baby Band-Aids for $1 today'

Read the JSON result out loud. Open the generated landing page or Vercel URL. Do not buy a domain. Do not post publicly. Only paste share copy if I explicitly approve the destination.
```

For another product, change only the quoted product phrase:

```text
cd /Users/alhinai/om1 && bash hackathon/ara_company_launcher/run_from_ara.sh 'Sell handmade matcha cookies for $1 today'
```

For live mode, set these environment variables before invoking Ara or ask Ara to export them in its shell:

```sh
export STRIPE_SECRET_KEY="sk_test_..."
export COMPANY_LAUNCH_LIVE_STRIPE=1
export COMPANY_LAUNCH_DEPLOY=1
export COMPANY_LAUNCH_PROD=0
```

Keep public posting disabled unless the destination is private and explicitly approved:

```sh
export COMPANY_LAUNCH_POST=0
```
