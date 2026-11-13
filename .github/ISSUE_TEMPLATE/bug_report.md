---
name: Bug report
about: A diagram fails to generate, or the skill guidance is wrong
title: "[BUG] "
labels: bug
assignees: ""
---

**Environment**
- Agent runtime: (opencode / Claude Code / Cursor / other)
- `staruml-mcp` version: (`npx staruml-mcp -V`)
- StarUML version:
- OS:

**What you asked the agent**
```
(the prompt you gave)
```

**The exact `code` sent to `generate_diagram`**
```
(paste the full Mermaid string — unreproducible without it)
```

**The exact error message**
```
(paste verbatim)
```

**What happened instead**
(what appeared in StarUML / nothing at all)

**Checklist**
- [ ] The `code` string starts with a supported keyword
- [ ] State diagram is ASCII-only
- [ ] No second colon in any transition label
