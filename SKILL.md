---
name: staruml
description: Use when creating, generating, fixing, or verifying UML diagrams in StarUML through the StarUML MCP server (generate_diagram, get_all_diagrams_info, get_diagram_image_by_id, get_current_diagram_info), when converting Mermaid to StarUML, or when a StarUML MCP call fails and the parser dialect needs debugging. Covers the exact Mermaid dialect StarUML accepts, the failure-safety protocol, and the visual verification workflow.
---

# StarUML MCP

Hard-won knowledge from driving the StarUML MCP server. StarUML accepts a **restricted Mermaid dialect** — standard Mermaid docs are NOT the source of truth. This skill is.

## 1. Tool contract (4 tools, nothing else)

| Tool | Purpose | Notes |
| ---- | ------- | ----- |
| `generate_diagram` | Create a new diagram from Mermaid code | Single param `code` (string). Creates a NEW diagram every call — never overwrites |
| `get_all_diagrams_info` | List all diagrams in open project | Returns `id`, `name`, `type`. Use to map IDs after batch generation |
| `get_current_diagram_info` | Info on currently open diagram | |
| `get_diagram_image_by_id` | Export diagram as image | Use for visual verification after generation |

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

1. Extract the source material first (PDFs via Python `pdfplumber`/`pymupdf` to PNG+text — PDFs are images, render pages to read diagrams).
2. Map each exercise to a diagram type (states → `stateDiagram-v2`, activity → `flowchart`, structure → `classDiagram`, interactions → `sequenceDiagram`).
3. Version A = faithful-to-correction structure; Version B = genuinely different approach (choice/verification state, time events, composite regions, fork/join, no-swimlanes) — not cosmetic label changes.
4. Generate sequentially, ASCII-only, escalating syntax complexity gradually, then verify all with images and report an ID table.
