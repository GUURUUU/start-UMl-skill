#!/usr/bin/env python3
"""Repo validator for start-UMl-skill.

Checks (all stdlib, no deps):
  1. Structural files exist (LICENSE, README, CHANGELOG, CONTRIBUTING, CI, templates).
  2. SKILL.md has valid frontmatter: name == staruml, non-empty description.
  3. Every examples/*.mmd starts with a supported diagram keyword.
  4. State-diagram examples obey the hard rules: ASCII-only, one colon per
     transition line, no `direction`, no frontmatter.
Exit code 0 = all green (what CI requires), 1 = failure with a reason list.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
PASSED: list[str] = []

KEYWORDS = {
    "classDiagram", "sequenceDiagram", "flowchart",
    "erDiagram", "mindmap", "requirementDiagram",
    "stateDiagram", "stateDiagram-v2",
}


def check(cond: bool, ok_msg: str, fail_msg: str) -> None:
    (PASSED if cond else ERRORS).append(ok_msg if cond else fail_msg)


def main() -> int:
    # 1. structural files
    required = [
        "README.md", "SKILL.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md", "SECURITY.md", "install.sh", "install.ps1",
        "docs/MANUAL_SETUP.md", "docs/AGENT_SETUP.md", "docs/MCP_LANGUAGE.md",
        "docs/SHOW_HN.md", "scripts/validate.py", "scripts/pdf_extract.py",
        ".github/workflows/ci.yml",
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ]
    for rel in required:
        check((ROOT / rel).is_file(), f"struct: {rel}", f"MISSING FILE: {rel}")

    check((ROOT / "assets/demo.gif").is_file(), "asset: demo.gif",
          "MISSING demo GIF (assets/demo.gif)")

    # 2. skill frontmatter
    skill = ROOT / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        check(bool(m), "skill: frontmatter present", "SKILL.md: missing YAML frontmatter")
        if m:
            fm = m.group(1)
            check(re.search(r"^name:\s*staruml\s*$", fm, re.M) is not None,
                  "skill: name == staruml", "SKILL.md frontmatter: name must be exactly 'staruml'")
            check(re.search(r"^description:\s*\S", fm, re.M) is not None,
                  "skill: description non-empty", "SKILL.md frontmatter: description must be non-empty")

    # 3+4. examples
    ex_dir = ROOT / "examples"
    mmds = sorted(ex_dir.glob("*.mmd")) if ex_dir.is_dir() else []
    check(len(mmds) >= 3, f"examples: {len(mmds)} diagram examples present",
          "examples: fewer than 3 .mmd files")

    for path in mmds:
        raw = path.read_text(encoding="utf-8")
        lines = [ln for ln in raw.splitlines() if ln.strip()]
        check(bool(lines), f"{path.name}: non-empty", f"{path.name}: empty file")
        if not lines:
            continue
        first = lines[0].strip()
        check(first.split()[0] in KEYWORDS, f"{path.name}: keyword '{first.split()[0]}'",
              f"{path.name}: first line must start with a supported keyword, got '{first}'")

        if first.startswith("stateDiagram"):
            body = lines[1:]
            check(not any(ln.strip().startswith("direction") for ln in body),
                  f"{path.name}: no direction directive",
                  f"{path.name}: 'direction' is not supported by StarUML")
            check(all(ln.isascii() for ln in lines),
                  f"{path.name}: ASCII-only",
                  f"{path.name}: non-ASCII characters are corrupted by StarUML's importer")
            for i, ln in enumerate(body, start=2):
                if "-->" in ln:
                    n = ln.count(":")
                    check(n <= 1, f"{path.name}:{i}: one colon max",
                          f"{path.name}:{i}: label contains {n} colons — parser splits on every ':'")
                check("%%{" not in ln and not ln.strip().startswith("%%"),
                      f"{path.name}:{i}: no directives",
                      f"{path.name}:{i}: directives (%%{{init}} etc.) are unsupported")

    # 5. README sanity: mentions demo gif + one-command install + one-liner
    readme = ROOT / "README.md"
    if readme.is_file():
        rtext = readme.read_text(encoding="utf-8")
        check("assets/demo.gif" in rtext, "readme: demo gif referenced",
              "README: must reference assets/demo.gif")
        check("curl -fsSL" in rtext and "install.sh" in rtext,
              "readme: one-command install present",
              "README: must contain the one-command install (curl ... install.sh)")
        check(rtext.lstrip("# \n").strip() != "", "readme: has headline",
              "README: empty?")

    # 6. no secrets checked in
    secret_pat = re.compile(
        r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})")
    offenders = []
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".sh", ".ps1", ".py", ".yml", ".yaml", ".mmd"}:
            if secret_pat.search(f.read_text(encoding="utf-8", errors="ignore")):
                offenders.append(str(f.relative_to(ROOT)))
    check(not offenders, "secrets: none found",
          f"SECRETS detected in: {offenders}")

    print(f"PASS {len(PASSED)} checks")
    for p in PASSED:
        print(f"  ok  {p}")
    if ERRORS:
        print(f"FAIL {len(ERRORS)} checks")
        for e in ERRORS:
            print(f"  XX  {e}")
        return 1
    print("ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
