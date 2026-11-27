---
name: cite-sync
description: 参考文献与引用管理. Insert and correct citations against supplied evidence, synchronize citation numbers and bibliography, deduplicate records, convert GB/T 7714 or APA 7, and deliver a revised manuscript with an auditable source map.
---

# Citation and reference management

Use for a manuscript, a literature library, or both. Read the actual task and inputs.
Preserve the manuscript's claims and put each citation beside the claim it supports.
Use Python 3.9+ and the dependencies in `requirements.txt` for DOCX and PDF.
Run offline by default. Add `--online` when registry verification is useful.

## Main workflow

1. **Run once on the case.** Discover Python and the installed Skill. The command
   detects the manuscript, libraries, target style, PDF sources and output contract.

   ```bash
   PY=$(command -v python3 || command -v python)
   for d in "${SKILL_DIR:-/skills/weekly-skill}" /skills/weekly-skill /app/submission /app/skills "$PWD"; do
     if [ -f "$d/scripts/cite.py" ]; then SKILL_DIR="$d"; break; fi
   done
   "$PY" "$SKILL_DIR/scripts/cite.py" run --case /input/case.json --work /app/work --out /app/output
   ```

   Read `/input/task.md` and the manifest of discovered inputs in `work/inventory.json`.
   If the inputs are ambiguous, use `--manuscript FILE`, repeated `--library FILE` or
   `--style gbt7714|apa7` with the same command. Explicit options take precedence.
   A library-only case produces formatted references and exports.

2. **Resolve priority citations together.** Read `work/priority_review.md` first
   for missing citations, mismatches and candidate source records. Use
   `work/claim_matrix.md` to locate additional occurrences required by the task.
   Open the underlying PDF or other source and inspect the relevant page, section,
   table or abstract. Preserve metrics, conditions, populations, direction and scope.
   A title match or registry hit can identify a publication. The relevant passage
   establishes whether that publication supports the sentence.

   - Record an insertion for the target sentence, or replace a wrong occurrence in place.
   - Key one compact `work/edits.json` by the sentence and occurrence IDs in the audit.
     A unique `text:...` prefix can also identify a sentence for insertion.
   - Use the indexed record IDs, original reference numbers or BibTeX keys.
     Add an evidence locator with the record and page or section for each change.
   - Mark uncertain passages `partial`, `mismatch` or `unverifiable` and give a reason.
     Leave unresolved cases in the review list when the material lacks support.
   - Use `record_overrides` only for values observed in a source. Set `_source` on each
     override. Use `force_merge` or `forbid_merge` only after comparing the actual works.

3. **Apply the reviewed batch.** Repeat the main command with
   `--edits /app/work/edits.json`. The renderer recomputes numbers from the actual
   final citation locations in the original manuscript and writes the synchronized list.
   Use `--online` on one pass when needed. Per-request and total network deadlines
   allow rendering to finish with an offline review record if a registry stalls.
   Use `--no-auto-move` if the case requires manual control of all marker placement.

4. **Verify the deliverables.** Check `review.md`, `run_report.json` when present, and
   the top-level names in `result.json`. Correct any remaining contract field using
   `work/contract_overrides.json` with its actual value and rerun when necessary.
   Nonblocking review findings produce a usable partial result. If a file is
   unreadable, record the limitation and retain the last successful deliverables.

## Six-action checklist

- [ ] **Insertion location** — each new or moved marker is adjacent to the supported assertion.
- [ ] **Full-text numbering** — first appearance agrees with the GB/T list, including captions
      and appendices. Reopen the written file and inspect the old-to-new mapping.
- [ ] **Deduplication** — compare DOI, title, authors and version. Inspect conflicting
      publisher identifiers and near matches before confirming a merge.
- [ ] **Format conversion** — GB/T 7714 uses synchronized numeric markers and type
      designators. APA 7 uses author–year citations and the matching alphabetical list.
- [ ] **Authentic sources** — confirm DOI, publisher record, arXiv or supplied PDF
      metadata. Record unavailable or contradictory evidence for review.
- [ ] **Claim–source match** — map the claim, citation and actual supporting passage.
      Check precise numbers, conditions and whether the source supports the whole claim.

## Short example

Fictional input has an uncited sentence indexed as `u2s0` and a PDF for `L1-1`
that directly supports it on page 4. The batch contains:

```json
{"add_citations":[{"sentence":"u2s0","refs":["L1-1"],"verdict":"supported","evidence":"source.pdf p.4, Results"}]}
```

The revised sentence gains a citation at its end and the same work appears in the list.
For a wrong existing marker, use `occurrences` keyed by its ID and set
`action: replace`, `refs`, `verdict` and `evidence`.

## Input and output details

- Manuscripts support Markdown, text, DOCX and LaTeX. Libraries support BibTeX,
  RIS, EndNote, NoteExpress, CSL-JSON and embedded reference lists. An explicitly\n  selected PDF manuscript is recovered as editable Markdown for layout review.
- Outputs include the editable revised manuscript, formatted list, BibTeX/RIS/CSL,
  citation and renumber maps, merge ledger, registry evidence, diff and review.
  DOCX PDF/PNG previews use LibreOffice when available, with a text-layout fallback.
- LaTeX emits synchronized citation keys and BibTeX. Compile with the target style
  to render the bibliography. Word field codes may be flattened and are reported.
- Registry metadata checks and lexical ranking do not prove a claim. Mark supplied
  material that cannot be read, OCR or matched. Report the unresolved review items
  and point to the editable artifact and previews in the final response.
