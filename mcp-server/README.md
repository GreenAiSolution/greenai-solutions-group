# greenaidigital.com MCP Server

A stdio [Model Context Protocol](https://modelcontextprotocol.io) server that exposes this repository — the live GreenAI Solutions website — as queryable tools for AI assistants like Claude. Every tool reads real files from the repo at call time; nothing is stubbed or cached.

## Tools

| Tool | What it does |
|---|---|
| `get_site_structure` | Lists every HTML page with its title, meta description, sitemap membership, and robots.txt status — a full map of the site. |
| `get_page_meta` | Returns one page's SEO/social metadata: title, description, keywords, canonical URL, Open Graph and Twitter tags. |
| `search_content` | Case-insensitive text search across all HTML/CSS/JS/MD files, with file + line number results. |
| `list_assets` | Lists non-HTML assets (images, CSS, JS, icons) with byte sizes, grouped by type — useful for page-weight audits. |
| `check_internal_links` | Scans every page's internal `href`/`src` references and reports any pointing at files that don't exist. |
| `get_sitemap_report` | Cross-checks `sitemap.xml` against the actual files: sitemap URLs with no file, and pages missing from the sitemap. |

## Setup

```bash
cd mcp-server
npm install
```

Add to Claude Code (from the repo root):

```bash
claude mcp add greenai-solutions-group -- node mcp-server/server.mjs
```

Or use the checked-in `.mcp.json` at the repo root — Claude Code picks it up automatically when you open the repo.

## Requirements

- Node.js 18+
