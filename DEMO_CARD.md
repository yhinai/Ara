# DEMO CARD — Ara x SF Hackathon (on-stage cheat sheet)

## 1. The Voice Command

**Say this to Ara, clearly, then pause:**

```text
Open Terminal and run exactly: cd /Users/alhinai/om1 && bash hackathon/ara_company_launcher/run_from_ara.sh 'Sell baby Band-Aids for $1 today' — do not ask follow-up questions.
```

- **Default product:** `baby Band-Aids`
- **Backup product:** `phone screen wipes`
- If no argument is passed, the script defaults to `Sell baby Band-Aids for $1 today`. Pre-copy your idea into the clipboard before going on stage; if Ara mishears, **paste** into Terminal instead of re-speaking.

## 2. What Happens

1. Ara opens Terminal and runs the script (~5 sec)
2. Stripe Payment Link API call → $1 link generated (~2 sec)
3. Static landing page built locally (~1 sec)
4. Vercel deploy → public URL (~15–30 sec)
5. TextEdit opens with the URL + share copy
6. Browser opens the deployed URL
7. Audience scans QR → pays → confetti on projector

**Total: ~45 seconds from voice command to live URL.**

## 3. The 90-Second On-Stage Pitch

**[5s — Hook, look at audience]**
> "I'm about to start a real company. With one sentence. Watch."

**[10s — Setup, face the Mac, speak to Ara]**
> "Ara: open Terminal and run my company launcher script with the idea: **Sell baby Band-Aids for one dollar today**. Don't ask questions."

**[30s — Filler while it runs, face audience]**
> "While that runs — Ara just opened my Terminal. It's hitting the Stripe Payment Link API for a real one-dollar checkout. Now it's templating a landing page. Now it's pushing to Vercel. No SDK, no glue code I wrote on the plane — it's just one voice line and ordinary APIs. [glance at screen] …and Vercel's deploying."

**[10s — Reveal, point at projector]**
> "There it is. Live URL. Real Stripe link. Real QR code. From one sentence, in under a minute."

**[25s — Live payment moment]**
> "Phones out — first person to scan this QR and pay one dollar gets the world's first baby Band-Aid from a company that did not exist 60 seconds ago." [wait for scan → confetti fires] "**Boom. First sale. The company is alive.**"

**[10s — Close]**
> "That's what builders do with AI now. Thank you."

## 4. Three Backup Ideas

| Idea phrase | Likely generated brand |
|---|---|
| **`Sell phone screen wipes for $1 today`** | *PhoneScreenWipes Co.* / *Wipe* |
| **`Sell handmade stickers for $1 today`** | *HandmadeStickers Co.* / *Sticker* |
| **`Sell a hand-written haiku for $1 today`** | *HandWrittenHaiku Co.* / *Haiku* |

All three are cheap, charming, $1-credible, and free of political / medical / sexual baggage.

## 5. Risk Hedges (read NOW, before going on stage)

- **No volunteer scans QR within 30 sec:** 2 friends planted in audience, phones unlocked, Stripe-ready.
- **Live demo crashes:** play the recorded clip from the H4 rehearsal.
- **Vercel slow / WiFi spotty:** tether off iPhone hotspot (pre-tested in H1).
- **Ara mishears:** the idea is pre-copied to clipboard — paste into Terminal instead of re-speaking.
- **Stripe still in test mode:** any `buy.stripe.com/test_…` URL = no real money. Swap to `sk_live_...` in `.env` BEFORE stage time.
- **QR too small to scan:** project the URL itself in 96pt below the QR.
- **First-sale confetti doesn't fire:** the live URL is still impressive — don't dwell on it, just move to the close.

## 6. After the Demo

- Thank audience members who paid (Stripe dashboard shows email).
- Refund all test/live payments via Stripe dashboard (one click each).
- DM the Ara team or post in **r/Aradotso** with the share copy.
- Pack up the `.app` launcher in case anyone wants to demo it themselves.

## 7. Emergency Reset

If anything is broken, run this in **your own** Terminal (not via Ara) — proves the pipeline works even if Ara fails:

```bash
cd /Users/alhinai/om1
bash hackathon/ara_company_launcher/run_from_ara.sh "Sell phone screen wipes for \$1 today"
```
