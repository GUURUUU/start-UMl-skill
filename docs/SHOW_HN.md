# Show HN draft (do not post before items 1–8 of the checklist are done; post on a weekday, then stay for the comments)

**Title (plain, no hype):**

> Show HN: start-UMl-skill – a skill file that teaches AI agents the StarUML MCP dialect

**Body:**

Hi HN! I kept losing hours to a silly problem: AI agents driving StarUML through MCP fail on the first try, every time. StarUML accepts a restricted Mermaid dialect that its docs (and Mermaid's docs) don't describe: a second colon in a transition label is a hard fail, accented characters get corrupted, `direction` and frontmatter break state diagrams, and there's no `activityDiagram` type at all.

So I turned my session notes into a single skill file any agent can install:

    curl -fsSL https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main/install.sh | bash

After restarting, opencode / Claude Code / Cursor agents generate correct StarUML diagrams on the first attempt — state machines, composite regions, activity diagrams with swimlanes — and they verify their own output with `get_diagram_image_by_id` instead of claiming success.

What's in the repo:
- `SKILL.md`: the dialect rules (8 supported keywords, ASCII-only, one-colon labels), a feature matrix of probed behavior, and a failure-safety protocol (one failure → stop and report, never retry-loop — your StarUML session stays clean)
- Setup guides for the MCP plumbing: StarUML API server (`:58321`), `npx -y staruml-mcp` (`:58323`), the optional 19-tool extension (`:58322`)
- Five ready-to-generate example diagrams and a CI validator for the skill itself

It's one Markdown file + two installer scripts + docs — MIT licensed. The MCP server itself is `staruml-mcp` by ezrabrilliant (npm), this is the knowledge layer on top of it.

Happy to answer questions — especially interested in whether other MCP servers would benefit from the same "dialect skill" pattern (probe the parser, encode the findings, ship the skill).
