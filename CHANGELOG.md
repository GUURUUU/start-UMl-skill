# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-11-21

### Added
- `SKILL.md` §10 — **full toolkit** captured from the TP4 session:
  - MCP call shapes with exact prefixed tool names (`staruml_generate_diagram`,
    `staruml_get_all_diagrams_info`, `staruml_get_current_diagram_info`,
    `staruml_get_diagram_image_by_id`), parameter names, and observed responses.
  - PDF → text + PNG extraction pipeline (`pdfplumber` / `pymupdf` / `PyPDF2`,
    150 dpi page rendering) with the `PYTHONIOENCODING=utf-8` Windows guard.
  - Image-based verification loop, batch todo tracking, and ID mapping by
    creation order.
  - Environment bring-up table (StarUML API server `:58321`, `staruml-mcp`
    `:58323`, extension `:58322`).
  - Publishing / CI toolkit: git, portable `gh`, GitHub device flow, REST
    payloads via file (PowerShell 5.1 quoting), Pillow assets, validator.
  - Manual GUI-only steps (rename F2, delete probe diagrams, Ctrl+S, re-accent).
- `SKILL.md` §11 — consolidated non-negotiables list.
- `scripts/pdf_extract.py` — standalone extractor: UTF-8 text with page markers
  plus one PNG per page; directory inputs; `--dpi`, `--text-only`,
  `--images-only`; graceful dependency fallbacks.
- `docs/MCP_LANGUAGE.md` — tool-surface table with exact observed responses
  and diagram types.
- README — toolkit quick-start block and the new script in "What's inside".

### Changed
- `SKILL.md` frontmatter description now covers the extraction toolkit and
  the prefixed MCP tool names.
- `scripts/validate.py` now requires `scripts/pdf_extract.py`, checks the
  toolkit section/tool names in `SKILL.md`, and byte-compiles the script.

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
