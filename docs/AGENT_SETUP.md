# Agent self-install instructions

**You are an AI agent reading this. Follow these steps to install the StarUML skill into yourself.** Do not skip the verification step.

## Step 1 — locate your skills directory

| Agent runtime | Skills path (create if missing) |
| ------------- | ------------------------------- |
| opencode (global) | `~/.config/opencode/skills/staruml/` |
| opencode (project) | `<project>/.opencode/skills/staruml/` |
| Claude Code | `~/.claude/skills/staruml/` |
| Generic (cross-agent) | `~/.agents/skills/staruml/` |

The folder name **must be `staruml`** and the file **must be named `SKILL.md`** (uppercase, exact).

## Step 2 — download the skill

```bash
mkdir -p <skills-path-from-step-1>
curl -fsSL https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main/SKILL.md \
  -o <skills-path-from-step-1>/SKILL.md
```

Or, if the repo is already cloned locally, copy the `SKILL.md` file from the repo root.

## Step 3 — verify the install

```bash
# must print: name: staruml
head -n 3 <skills-path>/SKILL.md

# must print valid YAML frontmatter with a description
python3 - <<'EOF'
import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
m=re.match(r'^---\n(.*?)\n---',t,re.S); assert m, 'missing frontmatter'
assert 'name: staruml' in m.group(1); assert 'description:' in m.group(1)
print('OK')
EOF
```

If your host shell is PowerShell, use `Get-Content <skills-path>\SKILL.md -TotalCount 3` instead.

## Step 4 — tell the user

Report exactly:

> Skill `staruml` installed to `<path>`. Restart me to load it, and make sure the `staruml-mcp` MCP server is registered (guide: `docs/MANUAL_SETUP.md` in the repo).

## Step 5 — after restart, your behavior contract

Once loaded, follow `SKILL.md` to the letter. Non-negotiables:

1. **First token of `code`** must be one of: `classDiagram`, `sequenceDiagram`, `flowchart`, `erDiagram`, `mindmap`, `requirementDiagram`, `stateDiagram`, `stateDiagram-v2`.
2. **State diagrams:** `stateDiagram-v2` first line, ASCII-only names/labels, **one colon per transition line**, no `direction`, no frontmatter, flat before nested.
3. **One `generate_diagram` failure → stop and report the exact error.** Single allowed retry only when the error names one invalid token. Never retry-loop.
4. **Always verify** after generation: `get_all_diagrams_info` → `get_diagram_image_by_id` per new diagram.
5. **Never claim** delete/rename/save capabilities — they don't exist in the baseline toolset.

## Step 6 — smoke test (only with StarUML running + MCP registered)

```
generate_diagram { "code": "stateDiagram-v2\n    [*] --> Ready\n    Ready --> [*]" }
get_all_diagrams_info
get_diagram_image_by_id <id-from-previous-call>
```

All three succeed → you are operational. Report the diagram ID to the user.
