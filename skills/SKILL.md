---
name: cite-sync
description: 参考文献与引用管理. Insert and correct citations against supplied evidence, synchronize citation numbers and bibliography, deduplicate records, convert GB/T 7714 or APA 7, and deliver a revised manuscript with an auditable source map.
---

# Citation and reference management

Use for a manuscript, a literature library, or both. Read the actual task and inputs.
Preserve the manuscript's claims and put each citation beside the claim it supports.
Use Python 3.9+ and the dependencies in `requirements.txt` for DOCX and PDF.

## Main workflow

1. **Read the task and generate the draft.** Read the original case and task before
   running the command. It discovers manuscripts, libraries, style, and supplied PDFs.
   This first pass writes a provisional manuscript, bibliography and review files.

   ```bash
   PY=$(command -v python3 || command -v python)
   for d in "${SKILL_DIR:-/skills/weekly-skill}" /skills/weekly-skill /app/submission /app/skills "$PWD"; do
     if [ -f "$d/scripts/cite.py" ]; then SKILL_DIR="$d"; break; fi
   done
   "$PY" "$SKILL_DIR/scripts/cite.py" run --case /input/case.json --work /app/work --out /app/output
   ```

   Check the discovered files in `work/inventory.json`. A usable draft with
   `partial` and exit 0 is the starting point for the source review below.
   If the inputs are ambiguous, use `--manuscript FILE`, repeated `--library FILE` or
   `--style gbt7714|apa7` with the same command. Explicit options take precedence.
   A library-only case produces formatted references and exports.

2. **Review the actual sources and prepare one edit batch.**
   - Start with `work/priority_review.md` for likely gaps and mismatches. Read
     `work/claim_matrix.md` for the full set of claims, including moved citations,
     body text, captions and appendices. Check the original manuscript for missed gaps.
   - Read the relevant pages of the supplied source. Judge the specific assertion
     at each marker, including a clause within a sentence when multiple markers occur.
   - In `/app/work/edits.json`, put new citations in `add_citations` and key existing
     decisions by ID in `occurrences`. IDs such as `ins_…` let you review automatic moves.
     Use canonical record IDs, original numbers or BibTeX keys from the audit.
   - For each evidence-backed decision put the file and page, figure, table or section
     in `evidence`, and explain the action in `note`. Use the specific library entry
     as a metadata locator when only metadata is supplied and say what remains unknown.
   - Use `action: replace` with `refs` on a wrong marker when the correct source
     has evidence. Use `drop_refs` with `refs` to remove unsupported sources from a
     cluster. If a source has a concrete authenticity defect, appears only in the
     manuscript and lacks corroboration, drop that reference from the marker and
     keep its record ID, the reason and the unsourced claim in the audit. An offline
     registry lookup alone cannot establish that a plausible record is invalid.
   - Set `verdict` to `supported`, `partial`, `mismatch` or `unverifiable`.
     Record the exact missing support in `note` for an unresolved decision.
   - Use `record_overrides` only for observed values and include `_source`.
     Use `force_merge` or `forbid_merge` after comparing the actual works.

3. **Render the reviewed draft.** Repeat the command with
   `--edits /app/work/edits.json`. It applies changes to the original, then computes
   the final numbering once. Use `--no-auto-move` if the task requires explicit moves.
   Run offline by default. Use `--online` only when allowed and useful for metadata.

4. **Check the final artifacts.** Open the revised manuscript, formal bibliography
   and `review.md`. Check citation placement and the post-write consistency result
   in `run_report.json`. When the case provides an output contract, the top-level keys
   of `result.json` must be exactly `case_id` plus the declared fields, with declared types.
   Status and uncertainty belong in `run_report.json` unless the contract declares them.
   Use generated `review.md`, `citation_map.json` and `verification.json` for evidence
   and uncertainties. Keep generated JSON intact. If a contract field remains unmapped,
   put its actual value in `work/contract_overrides.json` and render again.
   Confirm a new or replaced citation is visible in both `citation_map.json` and
   `changes`. The generated `review.md` lists evidence and unresolved decisions.
   With the usable deliverables checked, report remaining uncertainty and finish.

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
{"add_citations":[{"sentence":"u2s0","refs":["L1-1"],"verdict":"supported","evidence":"source.pdf p.4, Results","note":"Results directly support this sentence."}]}
```

The revised sentence gains a citation at its end and the same work appears in the list.
For a wrong existing marker, use `occurrences` keyed by its ID and set
`action: replace`, `refs`, `verdict` and `evidence`.

## Input and output details

- Manuscripts support Markdown, text, DOCX and LaTeX. Libraries support BibTeX,
  RIS, EndNote, NoteExpress, CSL-JSON and embedded reference lists. An explicitly
  selected PDF manuscript is recovered as editable Markdown for layout review.
- Outputs include the editable revised manuscript, formatted list, BibTeX/RIS/CSL,
  citation and renumber maps, merge ledger, registry evidence, diff and review.
  DOCX PDF/PNG previews use LibreOffice when available, with a text-layout fallback.
- LaTeX emits synchronized citation keys and BibTeX. Compile with the target style
  to render the bibliography. Word field codes may be flattened and are reported.
- Registry metadata checks and lexical ranking do not prove a claim. Mark supplied
  material that cannot be read, OCR or matched. Report the unresolved review items
  and point to the editable artifact and previews in the final response.
