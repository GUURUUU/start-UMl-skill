---
name: staruml
description: Use when creating, generating, fixing, or verifying UML diagrams in StarUML through the StarUML MCP server (staruml_generate_diagram, staruml_get_all_diagrams_info, staruml_get_diagram_image_by_id, staruml_get_current_diagram_info), when converting Mermaid to StarUML, when extracting exercises from PDFs before diagramming, or when a StarUML MCP call fails and the parser dialect needs debugging. Covers the exact Mermaid dialect StarUML accepts, the full working toolkit (PDF text/PNG extraction, Windows encoding guards, image verification, batch ID mapping), the failure-safety protocol, and the visual verification workflow.
---

# StarUML MCP

Hard-won knowledge from driving the StarUML MCP server. StarUML accepts a **restricted Mermaid dialect** — standard Mermaid docs are NOT the source of truth. This skill is.

**Version 1.1.0** — upgraded with the full toolkit used in the TP4 session (6 diagrams generated in one pass, zero retries on deliverables).

## 1. Tool contract (4 tools, nothing else)

Tool names as exposed by MCP hosts (opencode prefixes them with the server name; bare names work in clients that don't):

| Exposed name (opencode) | Bare name | Params | Purpose |
| --- | --- | --- | --- |
| `staruml_generate_diagram` | `generate_diagram` | `code` (string) | Create a NEW diagram from Mermaid code |
| `staruml_get_all_diagrams_info` | `get_all_diagrams_info` | none | List all diagrams in the open project |
| `staruml_get_current_diagram_info` | `get_current_diagram_info` | none | Info on the currently open diagram |
| `staruml_get_diagram_image_by_id` | `get_diagram_image_by_id` | `diagramId` (string) | Export one diagram as an image |

Exact observed responses:

```
staruml_generate_diagram {code: "stateDiagram-v2\n..."}      → "Diagram is successfully generated."
staruml_get_all_diagrams_info {}                             → All diagrams: [{"id":"AAAAAAGh0g...=","type":"UMLStatechartDiagram","name":"Statechart Diagram by Mermaid","description":""}, ...]
staruml_get_diagram_image_by_id {diagramId: "AAAAAAGh0g...="} → image payload
```

Diagram `type` values seen in a live project: `UMLClassDiagram`, `UMLStatechartDiagram`, `FCFlowchartDiagram`.

No delete, no rename, no save, no element-CRUD tools exist. Anything outside these four = report to user.

## 2. Supported first-line keywords (exact, case-sensitive)

`classDiagram` · `sequenceDiagram` · `flowchart` · `erDiagram` · `mindmap` · `requirementDiagram` · `stateDiagram` · `stateDiagram-v2`

**No `activityDiagram`.** Activity/flow diagrams must be built with `flowchart`. The first token of `code` must be one of these keywords — anything before it (frontmatter `---`, comments, blank BOM) fails instantly.

## 3. State diagrams (`stateDiagram-v2`) — hard rules

The only guaranteed-valid flat form:

```
stateDiagram-v2
    [*] --> Cree
    Cree --> HorsPret : unique
    Cree --> Disponible : non_unique
    Disponible --> HorsPret : hors_pret
    HorsPret --> Disponible : pret
    Disponible --> AEnlever : abime
    AEnlever --> [*] : supprime
    Disponible --> Prete : emprunte
    Prete --> Disponible : rapporte
    Prete --> Perdu : perdu
    Perdu --> Disponible : retrouve
    Perdu --> [*] : supprime
```

1. **First line must be `stateDiagram-v2`** (or another keyword above). No frontmatter, no `title`, no `---` block.
2. **No `direction LR/TB` directive.** The importer does not reliably support it.
3. **ASCII only** in state names and labels. `Cree` not `Créé`, `HorsPret` not `Hors Prêt`. Accented/multi-byte characters get corrupted in transit → invalid identifiers. (User can re-accent labels manually in the GUI afterward.)
4. **One colon per transition line.** The parser splits on `:` — a label like `: e1 : créé` mis-tokenizes and fails. Label = single identifier; use underscores: `: hors_pret`, `: after_1an_supprime`.
5. **Start minimal (flat).** Only attempt nested composite states after a flat diagram has succeeded at least once in the session.
6. No `%%` comments, `classDef`, `note`, or other directives.

## 4. Empirical parser findings (probed in a live session)

| Feature | Verdict |
| ------- | ------- |
| Minimal flat machine (`[*] --> A : label`) | ✅ works |
| Self-loops (`A --> A : do_sonner`) | ✅ works |
| `state "Hors Prêt" as HP` aliases + labels with `/`, `()`, `++` | ✅ parsed, but treat as **unstable** — prefer rule-compliant single-token labels |
| **Double colon in label** (`: e1 : créé`) | ❌ **hard fail** — most common breakage |
| Frontmatter / `direction` in state diagrams | ❌ fail |
| Nested composites: `state Outer { state Inner1 { ... } state Inner2 { ... } }` | ✅ works (incl. one `[*]` per composite, top-level `[*] --> Outer` + `Outer --> [*]`) |
| Three sibling top-level composites, no connecting transitions | ✅ works (renders side by side) |
| Sub-state name collisions across composites (e.g. `Sonnerie` in two regions) | ✅ worked in probes — keep an eye on it |
| Time event encoded as label (`after_1an_supprime`) | ✅ works as plain label |

Ordering discipline for complex state diagrams: flat probe → aliases/composites → regions. Escalate one level at a time.

## 5. Flowcharts for activity/flow diagrams

`flowchart` is the only way to get activity-diagram-like output. Verified working in one shot:

```
flowchart TB
    subgraph Bibliothecaire
        START((debut))
        ACQ([acquerir ouvrage])
        OUVR[[ouvrage]]
        MAJ([mettre a jour catalogue])
        ENR([enregistrer emprunt retour])
        DEC{controle}
        FIN((fin))
    end
    subgraph Gestionnaire
        INSC([inscrire adherent])
        ADH[[adherent]]
        CTRL([controler depassement delai])
        REL([relancer adherent])
    end
    START --> ACQ
    ACQ -.-> OUVR
    ACQ --> MAJ
    MAJ --> ENR
    ENR --> DEC
    DEC -->|anomalies| FIN
    DEC -->|delai depasse| REL
    DEC -->|si pas adherent| INSC
    INSC -.-> ADH
    ADH -.-> CTRL
    CTRL -->|delai depasse| REL
    REL --> FIN
```

Verified features: `subgraph` (swimlane groups), shapes `([stadium])` actions, `[[box]]` object nodes, `{diamond}` decisions, `((circle))` start/end, pipe edge labels `-->|guard|`, dotted arrows `-.->` object flows, plain rectangles for `fork`/`join` bars, cross-subgraph edges. Keep all text ASCII.

## 6. Failure-safety protocol (mandatory)

- **One `generate_diagram` failure → STOP.** Report the exact error message to the user. Do not retry variations without explicit user instruction.
- Single allowed self-retry: the error clearly names one invalid token → fix that token → retry **once**. Fails again → stop and report.
- Bisect only by proposing *new minimal attempts* to the user, never silent retry loops.
- When a task needs N diagrams, an unrelated next diagram may still be attempted (it is not a "variation" of the failed one) — but say so transparently.

## 7. Verification workflow

1. `generate_diagram` → expect "Diagram is successfully generated."
2. `get_all_diagrams_info` → map returned IDs to what was just generated (order of creation = order in list).
3. `get_diagram_image_by_id` per diagram → visually check states/edges/labels/composites.
4. Label overlaps in exported images are usually just low-res rendering — elements are draggable in the GUI. Structure errors ARE real: fix and regenerate (with user consent).

## 8. Housekeeping

- Every generated diagram is auto-named `"Statechart Diagram by Mermaid"` / `"Flowchart Diagram by Mermaid"` etc. — **no rename via MCP**. For multi-version tasks, tell the user to rename in Model Explorer (F2) and provide an ID ↔ version mapping table.
- No delete tool: any probe/test diagrams stay in the project. Minimize probes; list leftovers for manual cleanup (right-click → Delete Diagram).
- Exported images show `UNREGISTERED` watermarks if StarUML is unlicensed — cosmetic, not a diagram defect. Never "fix" it.
- The MCP operates on the **open project**; user must Ctrl+S in StarUML to persist.

## 9. Recipe: multi-exercise / multi-version tasks

For "make N versions of each exercise" requests:

1. Extract the source material first (PDFs via the toolkit in §10.2 — text extraction + page rendering to PNG).
2. Map each exercise to a diagram type (states → `stateDiagram-v2`, activity → `flowchart`, structure → `classDiagram`, interactions → `sequenceDiagram`).
3. Version A = faithful-to-correction structure; Version B = genuinely different approach (choice/verification state, time events, composite regions, fork/join, no-swimlanes) — not cosmetic label changes.
4. Generate sequentially, ASCII-only, escalating syntax complexity gradually, then verify all with images and report an ID table.

## 10. Toolkit — everything used to ship real diagram batches

### 10.1 MCP call shapes

Send the Mermaid as a single `code` string with `\n` newlines. Do not pass `title`, `direction`, or metadata as separate params — the tool has exactly one param.

```json
{"code": "stateDiagram-v2\n    [*] --> Cree\n    Cree --> Disponible : non_unique"}
```

After a batch, list once and map by creation order. The list includes probe diagrams too — count them when mapping IDs.

### 10.2 PDF → text + PNG pipeline (source extraction)

The `Read` tool may report "PDF read successfully" but the model cannot actually parse PDF content. Extract first:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/pdf_extract.py TP4-Enonc.pdf TP4-Correction.pdf --outdir .extract --dpi 150
```

`scripts/pdf_extract.py` in this repo does both halves:

| Dependency | Used for | Notes |
| --- | --- | --- |
| `pdfplumber` | text extraction per page | best for exercise statements |
| `pymupdf` (`fitz` / `import pymupdf`) | render pages → PNG | read correction diagrams visually |
| `PyPDF2` | fallback text | available on most machines |

Outputs: `<name>.txt` (UTF-8, page markers `=== PAGE N ===`) and `<name>_pN.png`. Then `Read` each PNG to see the correction diagrams.

If the scripts folder is unavailable, the minimal inline version:

```python
import pymupdf
doc = pymupdf.open("correction.pdf")
for i, page in enumerate(doc):
    page.get_pixmap(dpi=150).save(f"corr_p{i+1}.png")
```

### 10.3 Windows encoding guard (hard-won)

The default Windows console is cp1252. Printing extracted PDF text (arrows `→`, accents) crashes with `UnicodeEncodeError` mid-pipeline. Guards, in order of preference:

1. Set `$env:PYTHONIOENCODING='utf-8'` before Python.
2. Write extracted text to a file with `encoding='utf-8'`, then `Read` the file — never print it.
3. In scripts, `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`.

Do not trust console output for non-ASCII. File output is the source of truth.

### 10.4 Image verification

- Export each diagram with `staruml_get_diagram_image_by_id` and inspect the returned image directly.
- Check structure: all states present, every transition, composite frames, swimlane grouping, fork/join bars.
- Ignore cosmetic overlap: StarUML export renders nodes on top of each other until dragged in the GUI. Do not regenerate for overlap alone.
- Never "fix" the `UNREGISTERED` watermark — license artifact.

### 10.5 Batch tracking

Use the todo tool with one item per diagram (`Ex1 vA`, `Ex1 vB`, …), each `high` priority. Mark `in_progress` immediately before generating, `completed` only after the image check. For 6+ diagrams this prevents ID/version drift.

### 10.6 Environment bring-up (when tools are missing)

| Step | Command / action |
| --- | --- |
| StarUML ≥ 7 | install from https://staruml.io |
| Enable API server | `%APPDATA%\StarUML\settings.json` → `{"apiServer": true, "apiServerPort": 58321}`; restart StarUML |
| Verify API | `curl http://localhost:58321/` → `Hello from StarUML API Server!` |
| MCP server (HTTP) | `npx -y staruml-mcp --transport http` → `http://localhost:58323/mcp` |
| MCP server (stdio) | `npx -y staruml-mcp` |
| Full 19-tool set | install `staruml-mcp-extension` inside StarUML (`:58322`) |
| Verify tool list | ask the host "What StarUML tools do you have?" |

Ports: `58321` StarUML built-in API · `58322` extension · `58323` MCP HTTP listen.

### 10.7 Publishing / CI toolkit (used to ship this repo)

| Tool | Exact use | Gotcha |
| --- | --- | --- |
| `git` | `init -b main`, `add -A`, `commit` | LF→CRLF warnings on Windows are noise |
| `gh` CLI | repo create/push, topics, issues, releases | may be absent; `winget` may also be absent |
| Portable gh | download `gh_<ver>_windows_amd64.zip` from GitHub releases, `Expand-Archive` | binary is at `...\bin\gh.exe` — verify with `Get-ChildItem -Recurse -Filter gh.exe` |
| GitHub device flow | POST `https://github.com/login/device/code`, poll `access_token` | codes expire (~15 min); re-request on `expired_token` |
| `gh auth login --with-token` | pipe token from a temp file | delete the temp token file after use |
| `gh repo create --source . --remote origin --push` | one-shot publish | needs the local folder to be a git repo |
| REST API | topics, Discussions, secret scanning, releases | PowerShell 5.1 mangles inline JSON → write payload to a file and use `--input` |
| Pillow (`PIL`) | demo GIF + 1280×640 social preview | `Image.seek()` past `n_frames-1` raises `EOFError` — clamp indices |
| `scripts/validate.py` | 115+ structural/dialect checks | run before every commit; CI runs it on push |

### 10.8 Manual GUI steps (no MCP equivalent)

- Rename: Model Explorer → select diagram → `F2`.
- Delete probe diagrams: right-click → Delete Diagram.
- Save project: `Ctrl+S` (the MCP does not save).
- Re-accent labels: double-click state/transition text in the diagram editor.

## 11. Non-negotiables

1. `stateDiagram-v2` (or another supported keyword) must be the **first line** of `code`.
2. ASCII only for state names and transition labels.
3. One colon per transition line; single-token labels.
4. No `direction`, no `title`, no `---` frontmatter.
5. Flat diagram before composites; one escalation level at a time.
6. One failure → report the exact error and stop. Never retry-loop.
7. Verify every deliverable visually before declaring success.
