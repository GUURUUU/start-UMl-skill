# Security Policy

## Reporting a vulnerability

This repo contains documentation, Markdown skill files, and two small installer scripts — no runtime service, no secrets, no telemetry.

- For anything in **this repo** (installer script flaw, injection in docs, CI compromise): use **GitHub → Security → Report a vulnerability** (private advisory). Do not open a public issue for security reports.
- For vulnerabilities in the **MCP server** (`staruml-mcp`) or the **StarUML extension**: report upstream at https://github.com/ezrabrilliant/staruml-mcp/security.
- For StarUML itself: report to https://staruml.io.

## Known considerations

- The installers fetch only `SKILL.md` from this repo over HTTPS and write it into a user-owned skills folder. They never execute downloaded content.
- The API server on `:58321` and MCP HTTP on `:58323` bind to **localhost** by default; do not expose them to a network without understanding the consequences (anything that can reach them can drive your StarUML).

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅ |
| < 1.0   | ❌ |
