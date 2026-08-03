#!/usr/bin/env node
/**
 * MCP server for the GreenAI Solutions website (greenaidigital.com).
 *
 * Exposes the static site in this repository — pages, metadata, content,
 * assets, internal links, and the sitemap — as tools an AI assistant can
 * query over stdio. All tools read real files from the repo; nothing is
 * fabricated or cached.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, extname, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url))); // repo root
const SITE_URL = "https://greenaidigital.com";

// ---------- helpers ----------

const SKIP_DIRS = new Set([".git", "node_modules", "mcp-server", ".github"]);

function walk(dir, filter) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry) || entry.startsWith(".")) continue;
    const full = join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) out.push(...walk(full, filter));
    else if (!filter || filter(full)) out.push(full);
  }
  return out;
}

function rel(p) {
  return relative(ROOT, p);
}

function readPage(relPath) {
  const full = join(ROOT, relPath);
  if (!existsSync(full)) throw new Error(`Page not found: ${relPath}`);
  return readFileSync(full, "utf8");
}

function decodeEntities(s) {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&mdash;/g, "—")
    .replace(/&nbsp;/g, " ");
}

function extractMeta(html) {
  const meta = {};
  const title = html.match(/<title>([^<]*)<\/title>/i);
  if (title) meta.title = decodeEntities(title[1].trim());
  const metaTagRe = /<meta\s+[^>]*>/gi;
  for (const tag of html.match(metaTagRe) || []) {
    const name = tag.match(/(?:name|property)=["']([^"']+)["']/i);
    const content = tag.match(/content=["']([^"']*)["']/i);
    if (name && content) meta[name[1].toLowerCase()] = decodeEntities(content[1]);
  }
  const canonical = html.match(/<link\s+[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)["']/i)
    || html.match(/<link\s+[^>]*href=["']([^"']+)["'][^>]*rel=["']canonical["']/i);
  if (canonical) meta.canonical = canonical[1];
  return meta;
}

function htmlPages() {
  return walk(ROOT, (f) => extname(f) === ".html").map(rel).sort();
}

function text(obj) {
  return { content: [{ type: "text", text: typeof obj === "string" ? obj : JSON.stringify(obj, null, 2) }] };
}

// ---------- server ----------

const server = new McpServer({ name: "greenai-solutions-group", version: "1.0.0" });

server.registerTool(
  "get_site_structure",
  {
    title: "Get site structure",
    description:
      "List every HTML page in the repo with its <title> and meta description, plus whether it appears in sitemap.xml and whether robots.txt disallows it. Gives a full map of greenaidigital.com.",
    inputSchema: {},
  },
  async () => {
    let sitemapUrls = [];
    try {
      const sm = readFileSync(join(ROOT, "sitemap.xml"), "utf8");
      sitemapUrls = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
    } catch { /* no sitemap */ }
    let disallows = [];
    try {
      const robots = readFileSync(join(ROOT, "robots.txt"), "utf8");
      disallows = robots
        .split("\n")
        .filter((l) => l.toLowerCase().startsWith("disallow:"))
        .map((l) => l.split(":")[1].trim())
        .filter(Boolean);
    } catch { /* no robots */ }
    const pages = htmlPages().map((p) => {
      const meta = extractMeta(readFileSync(join(ROOT, p), "utf8"));
      const url = `${SITE_URL}/${p}`;
      return {
        file: p,
        title: meta.title || null,
        description: meta.description || null,
        inSitemap: sitemapUrls.some((u) => u === url || u.replace(/\/$/, "") === `${SITE_URL}/${p.replace(/index\.html$/, "")}`.replace(/\/$/, "")),
        robotsDisallowed: disallows.some((d) => `/${p}`.startsWith(d)),
      };
    });
    return text({ site: SITE_URL, pageCount: pages.length, pages });
  }
);

server.registerTool(
  "get_page_meta",
  {
    title: "Get page metadata",
    description:
      "Return the SEO/social metadata of one HTML page: title, meta description, keywords, canonical URL, and all Open Graph / Twitter tags.",
    inputSchema: { page: z.string().describe("Page path relative to repo root, e.g. 'index.html' or 'aether/index.html'") },
  },
  async ({ page }) => {
    const html = readPage(page);
    return text({ page, meta: extractMeta(html) });
  }
);

server.registerTool(
  "search_content",
  {
    title: "Search site content",
    description:
      "Case-insensitive substring search across all HTML, CSS, and JS files in the site. Returns file, line number, and the matching line (trimmed). Useful for finding where copy, prices, phone numbers, or code live.",
    inputSchema: {
      query: z.string().min(2).describe("Text to search for (case-insensitive substring)"),
      maxResults: z.number().int().min(1).max(200).optional().describe("Cap on returned matches (default 50)"),
    },
  },
  async ({ query, maxResults = 50 }) => {
    const files = walk(ROOT, (f) => [".html", ".css", ".js", ".md", ".xml", ".txt"].includes(extname(f)));
    const needle = query.toLowerCase();
    const matches = [];
    for (const f of files) {
      const lines = readFileSync(f, "utf8").split("\n");
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].toLowerCase().includes(needle)) {
          matches.push({ file: rel(f), line: i + 1, text: lines[i].trim().slice(0, 300) });
          if (matches.length >= maxResults) return text({ query, truncated: true, matches });
        }
      }
    }
    return text({ query, truncated: false, matches });
  }
);

server.registerTool(
  "list_assets",
  {
    title: "List site assets",
    description:
      "List non-HTML assets (images, CSS, JS, icons, fonts) with file sizes in bytes, grouped by type. Helps audit page weight and spot unused or oversized files.",
    inputSchema: {},
  },
  async () => {
    const assets = walk(ROOT, (f) => extname(f) !== ".html" && extname(f) !== "");
    const groups = {};
    for (const f of assets) {
      const ext = extname(f).slice(1).toLowerCase();
      (groups[ext] ||= []).push({ file: rel(f), bytes: statSync(f).size });
    }
    for (const ext of Object.keys(groups)) groups[ext].sort((a, b) => b.bytes - a.bytes);
    const totalBytes = assets.reduce((s, f) => s + statSync(f).size, 0);
    return text({ totalAssets: assets.length, totalBytes, byType: groups });
  }
);

server.registerTool(
  "check_internal_links",
  {
    title: "Check internal links",
    description:
      "Scan every HTML page for internal href/src references (pages, scripts, styles, images) and report any that point to files missing from the repo. External URLs, mailto:, tel:, and pure #anchors are skipped.",
    inputSchema: {},
  },
  async () => {
    const broken = [];
    let checked = 0;
    for (const page of htmlPages()) {
      const html = readFileSync(join(ROOT, page), "utf8");
      const refs = [...html.matchAll(/(?:href|src)=["']([^"']+)["']/gi)].map((m) => m[1]);
      for (const ref of refs) {
        if (/^(https?:|mailto:|tel:|sms:|javascript:|data:|#|\/\/)/i.test(ref)) continue;
        const clean = ref.split(/[?#]/)[0];
        if (!clean) continue;
        checked++;
        const base = clean.startsWith("/") ? join(ROOT, clean) : join(ROOT, dirname(page), clean);
        const candidates = [base, join(base, "index.html")];
        if (!candidates.some((c) => existsSync(c))) {
          broken.push({ page, ref });
        }
      }
    }
    return text({ internalRefsChecked: checked, brokenCount: broken.length, broken });
  }
);

server.registerTool(
  "get_sitemap_report",
  {
    title: "Sitemap coverage report",
    description:
      "Parse sitemap.xml and cross-check it against the HTML files actually in the repo: which sitemap URLs have no matching file, and which pages exist but are not listed in the sitemap.",
    inputSchema: {},
  },
  async () => {
    const sm = readFileSync(join(ROOT, "sitemap.xml"), "utf8");
    const urls = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
    const pages = htmlPages();
    const urlToFile = (u) => {
      let p = u.replace(SITE_URL, "").replace(/^\//, "");
      if (p === "" || p.endsWith("/")) p += "index.html";
      return p;
    };
    const missingFiles = urls.filter((u) => !existsSync(join(ROOT, urlToFile(u))));
    const listedFiles = new Set(urls.map(urlToFile));
    const notInSitemap = pages.filter((p) => !listedFiles.has(p));
    return text({ sitemapUrlCount: urls.length, urls, sitemapUrlsWithNoFile: missingFiles, pagesNotInSitemap: notInSitemap });
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("greenai-solutions-group MCP server running on stdio");
