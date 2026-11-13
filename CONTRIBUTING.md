# Contributing

Thanks for helping improve **start-UMl-skill**. This repo is mostly Markdown + one validator script, so contributions are low-ceremony.

## Local development

```bash
git clone https://github.com/GUURUUU/start-UMl-skill.git
cd start-UMl-skill
python scripts/validate.py     # must pass before every PR
```

Requirements: Python 3.9+ (stdlib only — no pip install needed).
To test the skill end-to-end you additionally need StarUML v7+ and Node.js 20+ (see `docs/MANUAL_SETUP.md`), but CI does not require them.

## Rules for SKILL.md changes

The skill encodes *observed behavior* of the StarUML MCP parser. Please keep these invariants:

1. **Every empirical claim stays labeled as empirical** — cite the probe/senario that produced it in your PR description.
2. **Hard rules stay hard** — the state-diagram template (ASCII-only, one colon per transition line, `stateDiagram-v2` first line) is load-bearing; don't relax it without evidence.
3. **No invented Mermaid syntax** — only document syntax verified against the real server (or clearly marked "unverified").
4. Keep the one-failure-stop protocol intact: it protects users' StarUML sessions from retry spam.

## How to test a parser claim

1. Start StarUML (API server enabled) and `npx -y staruml-mcp --transport http`.
2. Send the minimal `generate_diagram` call, then the variant you claim works/fails.
3. Screenshot/quote both results in the PR.

## Pull requests

- One topic per PR.
- Run `python scripts/validate.py` locally; CI must be green.
- Update `CHANGELOG.md` under an `## [Unreleased]` heading.
- Sign off DCO: `git commit -s` (or add `Signed-off-by:` trailer).

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include the **exact Mermaid code** and the **exact error message** — parser issues are unreproducible without them.
