# Manual setup — StarUML + MCP + agent (human guide)

Everything you need to go from zero to *"generate UML diagrams by chat"*.

## 0. Architecture (what talks to what)

```
AI agent ──MCP──► staruml-mcp (npm) ──HTTP──► StarUML
                                          :58321 (built-in API, 4 tools)
                                          :58322 (extension, +15 tools)
:58323 = staruml-mcp HTTP listen port
```

| Component | Runs where | Needed for |
| --------- | ---------- | ---------- |
| StarUML v7.0.0+ | your desktop | everything |
| StarUML **API server** (built-in) | inside StarUML | the 4 Mermaid tools |
| `staruml-mcp` (npm) | your machine, via `npx` | the MCP bridge |
| `staruml-mcp-extension` (optional) | inside StarUML | +15 tools: save/open project, element CRUD, execute commands |
| This skill (`SKILL.md`) | your agent's skills folder | making the agent use it all *correctly* |

## 1. Install StarUML and enable the API server

1. Download StarUML ≥ 7.0 from https://staruml.io and install it.
2. Edit its settings file:
   - **Windows:** `%APPDATA%\StarUML\settings.json`
   - **macOS:** `~/Library/Application Support/StarUML/settings.json`
   - **Linux:** `~/.config/StarUML/settings.json`
3. Add / merge these keys:
   ```json
   {
     "apiServer": true,
     "apiServerPort": 58321
   }
   ```
4. **Restart StarUML** and leave it open with a project loaded.
5. Verify:
   ```bash
   curl http://localhost:58321/
   # → "Hello from StarUML API Server!"
   ```

## 2. Start the MCP server

Node.js 20+ required.

```bash
# Option A — stdio (Claude Desktop, Cursor, VS Code, Codex CLI)
npx -y staruml-mcp

# Option B — HTTP (opencode, Claude Code, anything that speaks HTTP MCP)
npx -y staruml-mcp --transport http
# → listens on http://localhost:58323/mcp
```

Useful flags: `--port 58323`, `--api-port 58321`, `--ext-port 58322`, `--api-host http://localhost`.

## 3. Register the server with your agent

### opencode (global `~/.config/opencode/opencode.json` or project `opencode.json`)

```json
{
  "mcp": {
    "staruml": {
      "type": "local",
      "command": ["npx", "-y", "staruml-mcp"],
      "enabled": true,
      "environment": {}
    }
  }
}
```
(HTTP variant: `"type": "remote", "url": "http://localhost:58323/mcp"` — start the server yourself first.)
Then **restart opencode** — MCP config is read at startup.

### Claude Code (HTTP, recommended)

```bash
npx -y staruml-mcp --transport http          # keep this terminal running
claude mcp add --transport http staruml http://localhost:58323/mcp
```

### Claude Desktop (stdio)

`%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "staruml": {
      "command": "npx",
      "args": ["-y", "staruml-mcp"]
    }
  }
}
```

### Cursor / VS Code Copilot / Codex CLI

Point the client at `npx -y staruml-mcp` (stdio) or `http://localhost:58323/mcp` (HTTP), per your client's MCP settings UI.

## 4. Install the skill (the whole point of this repo)

```bash
curl -fsSL https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main/install.sh | bash      # Linux/macOS
irm https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main/install.ps1 | iex            # Windows
```

Manual alternative — copy `SKILL.md` from this repo into:
- opencode: `~/.config/opencode/skills/staruml/SKILL.md`
- Claude Code: `~/.claude/skills/staruml/SKILL.md`
- generic agents: `~/.agents/skills/staruml/SKILL.md`

Restart the agent. Ask: *"What StarUML tools do you have?"* — you should get the 4 tools back.

## 5. Optional: the full 19-tool set

Install `staruml-mcp-extension` **inside StarUML**:

> Tools → Extension Manager → **Install From URL** → `https://github.com/ezrabrilliant/staruml-mcp-extension`

This adds project save/open, element CRUD, native typed diagram creation and `execute_command` (tools `get_all_commands`, `execute_command`, `get_project_info`, `save_project`, `save_project_as`, `new_project`, `open_project`, `get_element_by_id`, `find_elements`, `create_element`, `update_element`, `delete_element`, `create_element_with_view`, `create_edge_with_view`, `create_diagram`, `switch_diagram`, `close_diagram`…). Without it, the 4 Mermaid tools still work — graceful degradation.

## 6. Verification checklist

| Step | Expected |
| ---- | -------- |
| `curl http://localhost:58321/` | `"Hello from StarUML API Server!"` |
| Agent: "What StarUML tools do you have?" | lists `generate_diagram` + 3 info tools |
| Agent: `generate_diagram` with any `examples/*.mmd` content | "Diagram is successfully generated." + a new diagram in StarUML |
| Agent: `get_diagram_image_by_id` | image of the new diagram returned |

## 7. Troubleshooting

| Symptom | Cause / fix |
| ------- | ----------- |
| `Failed to execute command(/generate_diagram)` | Label contains a second `:` or non-ASCII characters — see `docs/MCP_LANGUAGE.md` |
| Tools listed but generation hangs | StarUML closed or API server off — re-check `settings.json` + keep StarUML open |
| MCP server not visible in agent | Config file edited in wrong scope, or agent not restarted |
| Diagrams pile up named "…by Mermaid" | By design: no rename via MCP — rename in Model Explorer (F2), save with Ctrl+S |
| `UNREGISTERED` watermark on exported images | StarUML unlicensed — cosmetic only |

## 8. Version notes

- Written and verified against `staruml-mcp` **0.3.3** (npm), StarUML v7, opencode + Claude Code clients, Windows.
- Ports 58321/58322/58323 are the defaults everywhere; keep them consistent.
