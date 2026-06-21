# AETHER by GreenAI

GreenAI's flagship product site — a fully 3D, immersive sales experience for our high-ticket custom AI Agent service.

**Local dev:** `python3 -m http.server 8093 --directory .` then visit http://localhost:8093

---

## What you need to do once before going live

The site is fully built. To make it sell real orders to real customers, you (Jaden) need to do **three small setup steps**. None requires code; each takes a few minutes.

### 1. Turn on form submissions (5 minutes)

The onboarding modal already POSTs every intake to **jaden@greenaidigital.com** via [Formsubmit.co](https://formsubmit.co) — a free, no-signup forwarder.

**To activate:**
1. The first time someone submits the form, you'll get an email titled *"Confirm your email at FormSubmit"* — **click the link inside.** That's it. Forever.
2. After that, every intake from the site comes straight to your inbox with the prospect's company, role, target outcome, connectors they want, and chosen template.

If you'd rather route submissions somewhere else later (Notion, Airtable, Slack), edit `FORM_ENDPOINT` at the top of `app.js`.

### 2. Wire up Stripe (15 minutes)

Currently the "Book a call" / "Book a strategy call" / "Contact sales" buttons open the onboarding modal directly so you can demo the experience. To take real money:

1. Log in to your [Stripe dashboard](https://dashboard.stripe.com) → **Products** → **Add product**
2. Create three products:
   - **Spark** — recurring $997/mo (6-month minimum, no setup fee)
   - **Catalyst** — recurring $2,997/mo + one-time setup $4,997
   - **Momentum** — recurring $7,997/mo + one-time setup $9,997
   - *(Enterprise stays as a mailto/contact link — close those by phone)*
3. For each, click **Create payment link** and copy the URL (looks like `https://buy.stripe.com/abc123`).
4. In Stripe's payment link settings, set the **"After payment" → Confirmation page** to:
   ```
   https://yourdomain.com/?onboard=1&plan=spark
   ```
   (Use the matching plan slug per link: `spark`, `catalyst`, `momentum`)
5. Open `index.html` and paste each URL into the `data-stripe` attribute on the matching pricing card's button:
   ```html
   <a class="cta-primary buy-btn" data-stripe="https://buy.stripe.com/abc123">Book a strategy call</a>
   ```

Once `data-stripe` is set, the button takes the user to Stripe Checkout. On successful payment, Stripe sends them back to your site with `?onboard=1` — the onboarding modal auto-opens and the intake flow runs.

### 3. Deploy the site (10 minutes)

Easiest options:
- **Netlify Drop** — drag the `greenai-aether` folder onto https://app.netlify.com/drop → done, gives you a live URL in 30 seconds. Add a custom domain in settings.
- **GitHub Pages** — push to a new repo, enable Pages on the `master` branch. (Same flow as your existing greenaidigital.com.)
- **Subdomain on greenaidigital.com** — easiest if you want to keep your current site too. Aim for `aether.greenaidigital.com`.

---

## How we actually deliver agents in 48 hours

See `agents/sales-sdr/` for the first complete agent template:
- **`system-prompt.md`** — the production-grade Claude prompt
- **`integration-spec.md`** — required connectors, per-client variables, n8n workflow shape, and the hour-by-hour delivery checklist

That's the artifact we ship for every Catalyst order. We'll add 5–7 more templates over the next two weeks (Inbox Triage, Support Deflector, Ops Automator, Reporting Agent, AP/AR Clerk, Recruiting Sourcer) — each one is one more agent we can resell at $2,497/mo with zero per-client build cost.

### One-time fulfillment infra to set up
| Tool | Purpose | Cost | Time |
|---|---|---|---|
| [n8n Cloud](https://n8n.cloud) | Agent runtime — one workspace per client | $20/mo | 30 min |
| [Anthropic API](https://console.anthropic.com) | Claude key (the brain) | Usage-based | 5 min |
| [Pipedream Connect](https://pipedream.com/connect) | OAuth into client tools | Free tier | 1 hr |
| [Supabase](https://supabase.com) | Per-client state + vector memory | Free tier | 30 min |
| [Langfuse](https://langfuse.com) | Trace + monitor every agent action | Free tier | 20 min |

Total monthly fixed cost to be in business: **~$20**. Per-client variable cost: ~$30–80/mo in API spend (you charge $2,497+/mo).

---

## File map

```
greenai-aether/
├── index.html          ← markup + scroll panels + onboarding modal
├── styles.css          ← design system + 3D scene styles + pricing + modal
├── app.js              ← Three.js scene + scroll cinematics + modal controller + form submit
├── README.md           ← this file
└── agents/
    └── sales-sdr/
        ├── system-prompt.md      ← the actual Claude prompt we ship per client
        └── integration-spec.md   ← connectors, variables, delivery checklist
```

---

*Built immersive. 2026 · GreenAI Solutions · jaden@greenaidigital.com*
