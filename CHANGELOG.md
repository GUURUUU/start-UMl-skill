# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-11-13

### Added
- `SKILL.md` — the complete StarUML MCP skill: 4-tool contract, 8 supported
  Mermaid keywords, state-diagram hard rules (ASCII-only, one-colon labels,
  no `direction`/frontmatter), empirical parser findings, flowchart recipes
  for activity diagrams, failure-safety protocol, verification workflow,
  housekeeping notes, multi-exercise recipe.
- One-command installers: `install.sh` (Linux/macOS/WSL) and `install.ps1`
  (Windows PowerShell), targeting opencode / Claude Code / generic
  `~/.agents/skills` layouts.
- `docs/MANUAL_SETUP.md` — full human setup guide: StarUML API server,
  `staruml-mcp` npm server (stdio + HTTP), per-client registration
  (opencode, Claude Code, Claude Desktop, Cursor, VS Code Copilot, Codex),
  the `staruml-mcp-extension` for the full 19-tool set.
- `docs/AGENT_SETUP.md` — self-install instructions written for AI agents.
- `docs/MCP_LANGUAGE.md` — StarUML Mermaid dialect reference + failure table.
- `docs/SHOW_HN.md` — Show HN launch draft.
- `examples/` — five ready-to-generate diagrams (flat state machine,
  concurrent composite regions, activity swimlanes, fork/join activity,
  class diagram).
- `scripts/validate.py` + GitHub Actions CI (`ci.yml`) validating the skill
  frontmatter, the ASCII/one-colon rules, and repo structural files.
- Issue templates (bug report, feature request), PR template,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, MIT `LICENSE`.
- Repo assets: animated demo GIF and 1280×640 social preview.

[1.0.0]: https://github.com/GUURUUU/start-UMl-skill/releases/tag/v1.0.0
