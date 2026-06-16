/**
 * GreenAI Studio — Cloudflare Worker Backend
 *
 * Endpoints:
 *   POST /api/text   → proxies to Anthropic Claude (server-side ANTHROPIC_API_KEY)
 *   POST /api/image  → generates images via Pollinations.ai (free, no key) with optional img2img-style logo prompt
 *   GET  /api/health → status check
 *
 * Auth:
 *   Every request must include:  Authorization: Bearer <STUDIO_ACCESS_TOKEN>
 *   STUDIO_ACCESS_TOKEN is set as a Cloudflare secret.  The studio.html front-end
 *   sends it after the visitor enters the access code "greenai2026".
 *
 * Required environment / secrets (set with `wrangler secret put`):
 *   ANTHROPIC_API_KEY     — your Anthropic key (sk-ant-...)
 *   STUDIO_ACCESS_TOKEN   — long random string the front-end will send as Bearer
 *
 * Optional vars (wrangler.toml [vars] section):
 *   ALLOWED_ORIGIN        — defaults to "https://greenaidigital.com"
 *   CLAUDE_MODEL          — defaults to "claude-haiku-4-5-20251001"
 */

const DEFAULT_MODEL = "claude-haiku-4-5-20251001";

function corsHeaders(env, origin) {
  const allowed = (env.ALLOWED_ORIGIN || "https://greenaidigital.com").split(",").map(s => s.trim());
  // Allow localhost for dev
  const ok = allowed.includes(origin) || /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin || "");
  return {
    "Access-Control-Allow-Origin": ok ? origin : allowed[0],
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function json(data, status, extraHeaders) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...(extraHeaders || {}) },
  });
}

function checkAuth(req, env) {
  const h = req.headers.get("Authorization") || "";
  const m = h.match(/^Bearer\s+(.+)$/i);
  if (!m) return false;
  return m[1] === env.STUDIO_ACCESS_TOKEN;
}

async function handleText(req, env, cors) {
  let body;
  try { body = await req.json(); } catch { return json({ error: "Invalid JSON" }, 400, cors); }
  const prompt = body.prompt;
  const maxTok = Math.min(parseInt(body.max_tokens || 1500, 10), 8000);
  if (!prompt || typeof prompt !== "string") return json({ error: "Missing prompt" }, 400, cors);
  if (!env.ANTHROPIC_API_KEY) return json({ error: "Server not configured: ANTHROPIC_API_KEY missing" }, 500, cors);

  const model = env.CLAUDE_MODEL || DEFAULT_MODEL;
  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model,
      max_tokens: maxTok,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!upstream.ok) {
    const err = await upstream.json().catch(() => ({}));
    return json({ error: err.error?.message || `Upstream ${upstream.status}` }, upstream.status, cors);
  }
  const data = await upstream.json();
  const text = data.content?.[0]?.text || "";
  return json({ text, model }, 200, cors);
}

async function handleImage(req, env, cors) {
  let body;
  try { body = await req.json(); } catch { return json({ error: "Invalid JSON" }, 400, cors); }
  const prompt = (body.prompt || "").trim();
  const width = Math.min(Math.max(parseInt(body.width || 1080, 10), 256), 2048);
  const height = Math.min(Math.max(parseInt(body.height || 1080, 10), 256), 2048);
  const count = Math.min(Math.max(parseInt(body.count || 1, 10), 1), 4);
  const includeLogo = !!body.include_logo;
  if (!prompt) return json({ error: "Missing prompt" }, 400, cors);

  // Pollinations.ai — free, no key required, supports Flux model
  // Logo "img2img" trick: we append a strong text instruction to the prompt
  // because Pollinations doesn't accept reference image uploads on its free endpoint.
  const logoHint = includeLogo
    ? ", incorporate a subtle hexagonal emerald and gold logo crest watermark in lower right corner, brand mark for GreenAI Solutions Team"
    : "";
  const finalPrompt = prompt + logoHint;
  const encoded = encodeURIComponent(finalPrompt);

  const urls = [];
  for (let i = 0; i < count; i++) {
    const seed = Math.floor(Math.random() * 999999);
    urls.push(`https://image.pollinations.ai/prompt/${encoded}?width=${width}&height=${height}&seed=${seed}&nologo=true&model=flux&enhance=true`);
  }
  return json({ images: urls, prompt: finalPrompt }, 200, cors);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin") || "";
    const cors = corsHeaders(env, origin);

    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    if (url.pathname === "/api/health") {
      return json({ ok: true, has_key: !!env.ANTHROPIC_API_KEY, model: env.CLAUDE_MODEL || DEFAULT_MODEL }, 200, cors);
    }

    if (!checkAuth(req, env)) return json({ error: "Unauthorized" }, 401, cors);

    if (req.method === "POST" && url.pathname === "/api/text")  return handleText(req, env, cors);
    if (req.method === "POST" && url.pathname === "/api/image") return handleImage(req, env, cors);

    return json({ error: "Not found" }, 404, cors);
  },
};
