# GreenAI Studio — Backend Worker

This is the Cloudflare Worker that powers the AI tools in `studio.html`. Your Anthropic API key lives here on the server — visitors never see or paste it. They just enter the access code on the studio login screen.

## One-time setup (≈ 5 minutes)

1. **Sign up free** at https://dash.cloudflare.com/sign-up — no credit card required.
2. **Get an Anthropic key** at https://console.anthropic.com → API Keys → Create Key (starts with `sk-ant-`).
3. **Pick a long random access token** — anything 32+ chars works. This is what visitors don't see; the front-end sends it for you. Example: `openssl rand -hex 32` or just mash the keyboard.

## Deploy

From this `worker/` folder:

```bash
npm install
npx wrangler login                 # opens browser, logs into your Cloudflare account
npx wrangler secret put ANTHROPIC_API_KEY      # paste your sk-ant-... key
npx wrangler secret put STUDIO_ACCESS_TOKEN    # paste your long random token
npx wrangler deploy
```

Wrangler will print a URL like:
```
https://greenai-studio-api.<your-subdomain>.workers.dev
```

## Wire the studio to your worker

Open `studio.html` in the repo and find these two constants near the top of the `<script>` block:

```js
const STUDIO_API_URL = "https://greenai-studio-api.YOUR-SUBDOMAIN.workers.dev";
const STUDIO_API_TOKEN = "YOUR_STUDIO_ACCESS_TOKEN";
```

Replace with your actual worker URL and the access token you set above. Commit and push — GitHub Pages redeploys in ~1 minute and the studio is live.

## Updating / rotating keys

```bash
npx wrangler secret put ANTHROPIC_API_KEY       # overwrites the old one
npx wrangler deploy
```

## Cost

Cloudflare Workers free tier = 100,000 requests/day, more than enough. Anthropic charges for token usage on your key (Haiku 4.5 is ~$0.25 per million input tokens).

## Endpoints

- `GET  /api/health` — quick status check (no auth)
- `POST /api/text`   — Claude text generation. Body: `{ prompt, max_tokens }`
- `POST /api/image`  — Pollinations image generation. Body: `{ prompt, width, height, count, include_logo }`

Every request except `/api/health` needs `Authorization: Bearer <STUDIO_ACCESS_TOKEN>`.
