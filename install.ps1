# start-UMl-skill installer (Windows PowerShell)
# Usage:
#   irm https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main/install.ps1 | iex
#   irm .../install.ps1 | iex; Install-StarUmlSkill -Target claude
param(
    [ValidateSet("opencode", "claude", "agents")]
    [string]$Target = "opencode"
)

$ErrorActionPreference = "Stop"
$repoBase = if ($env:STARUML_SKILL_REPO) { $env:STARUML_SKILL_REPO } else { "https://raw.githubusercontent.com/GUURUUU/start-UMl-skill/main" }

$dest = switch ($Target) {
    "opencode" { Join-Path $env:USERPROFILE ".config\opencode\skills\staruml" }
    "claude"   { Join-Path $env:USERPROFILE ".claude\skills\staruml" }
    "agents"   { Join-Path $env:USERPROFILE ".agents\skills\staruml" }
}

if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
Invoke-WebRequest -Uri "$repoBase/SKILL.md" -OutFile (Join-Path $dest "SKILL.md") -UseBasicParsing

Write-Host "OK  skill installed: $dest\SKILL.md"
Write-Host "    Restart your agent, then ask: \"What StarUML tools do you have?\""
Write-Host "    MCP plumbing guide: https://github.com/GUURUUU/start-UMl-skill/blob/main/docs/MANUAL_SETUP.md"
