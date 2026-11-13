## Description

(What does this PR change and why? Link the issue with `Fixes #N` if applicable.)

## Type of change

- [ ] Bug fix (skill guidance was wrong / validator false-positive)
- [ ] New parser finding for `SKILL.md` (must include probe evidence: MCP version, minimal snippet, observed result)
- [ ] Docs / examples
- [ ] Tooling (installers, CI, validator)
- [ ] Breaking change (hard rules relaxed or changed)

## Checklist

- [ ] `python scripts/validate.py` passes locally
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] SKILL.md parser claims are empirically labeled (no invented syntax)
- [ ] Hard rules (ASCII-only, one colon per transition line, `stateDiagram-v2` first) untouched unless breaking
- [ ] No secrets added
