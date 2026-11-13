#!/usr/bin/env bash
# start-UMl-skill installer — drops the StarUML skill into your AI agent's skills folder.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main/install.sh | bash
#   curl ... | bash -s -- --target claude     # install for Claude Code instead of opencode
set -euo pipefail

REPO_BASE="${STARUML_SKILL_REPO:-https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main}"
TARGET="opencode"

for arg in "$@"; do
  case "$arg" in
    --target=*) TARGET="${arg#*=}" ;;
    --target)   shift_arg=1 ;;
    opencode|claude|agents) [ "${shift_arg:-0}" = "1" ] && TARGET="$arg" ;;
    *) echo "Unknown argument: $arg (use --target opencode|claude|agents)"; exit 1 ;;
  esac
done

case "$TARGET" in
  opencode) DEST="${HOME}/.config/opencode/skills/staruml" ;;
  claude)   DEST="${HOME}/.claude/skills/staruml" ;;
  agents)   DEST="${HOME}/.agents/skills/staruml" ;;
  *) echo "Unknown target: $TARGET"; exit 1 ;;
esac

mkdir -p "$DEST"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$REPO_BASE/SKILL.md" -o "$DEST/SKILL.md"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$DEST/SKILL.md" "$REPO_BASE/SKILL.md"
else
  echo "Need curl or wget." >&2; exit 1
fi

echo "OK  skill installed: $DEST/SKILL.md"
echo "    Restart your agent, then ask: \"What StarUML tools do you have?\""
echo "    MCP plumbing guide: https://github.com/GUURUUU/start-UMl-skill/blob/main/docs/MANUAL_SETUP.md"
