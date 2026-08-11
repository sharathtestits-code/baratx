# Cloudflare MCP (Cursor)

Config: `.cursor/mcp.json`

| Server | URL | Use |
| --- | --- | --- |
| `cloudflare` | https://mcp.cloudflare.com/mcp | Full Cloudflare API (DNS, Pages, zones) via Code Mode |
| `cloudflare-docs` | https://docs.mcp.cloudflare.com/mcp | Live Cloudflare docs |
| `cloudflare-dns-analytics` | https://dns-analytics.mcp.cloudflare.com/mcp | DNS analytics / debug |

## Auth
First tool call opens **OAuth** — sign in with the Cloudflare account that owns `barathx.com` / Pages project `baratx`.

## Cloud Agents
Project `.cursor/mcp.json` is for Cursor Desktop/IDE. For **Cloud Agents**, also add the same servers under Cursor Dashboard → Integrations & MCP (or Cloud Agents MCP settings), then complete OAuth for this environment.

## Goal for BarathX outage
After auth: list zone NS for `barathx.com`, confirm Cloudflare NS, fix custom domain / DNS records so apex stops redirecting to Porkbun Easy Links (`*.l.ink`).
