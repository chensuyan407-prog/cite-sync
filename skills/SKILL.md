---
name: cite-sync
description: 参考文献与引用管理 / citation & reference-list management for a manuscript (.md/.txt/.docx/.tex) plus reference libraries (BibTeX, RIS, EndNote .enw incl. CNKI export, NoteExpress, CSL-JSON, or the manuscript's own list). Use when a task asks to insert or fix citations, renumber [n] markers after insert/delete/reorder, sync the in-text numbers with the reference list, de-duplicate entries (zh/en titles, preprint vs published, different database exports), convert to GB/T 7714-2015 or APA 7 / BibTeX / RIS, verify that references exist (DOI/Crossref/arXiv) and that each cited sentence matches its source. Scripts keep a ledger (merge rule per pair, old->new number map, per-citation verdict, every change) and re-parse the written file to prove numbering and list are consistent; result.json reports honest status and what needs a human.
---

# cite-sync (v0.1.0)

The scripts do the bookkeeping that LLM editing gets wrong (numbering, list sync, de-duplication, formatting,
registry lookups); **you** do the judgement (does this sentence really need / match this source?).
Python 3.9+ stdlib; `python-docx` only for .docx. `SKILL_DIR` = directory of this file (`/skills/weekly-skill`).
Budget: about 5–10 model requests. Save early: `init` already writes a valid partial `result.json`.

## Workflow

1. **Init** – finds manuscript, libraries, PDFs, `task.md`, contract fields; writes a partial result.
   ```bash
   python $SKILL_DIR/scripts/cite.py init --case /input/case.json --out /app/output --work /app/work
   ```
   Read `task.md` and `case.json` yourself: target style (GB/T 7714-2015 → `gbt7714`, APA → `apa7`),
   required output fields, which file is the manuscript. Do not trust file labels; open the files.
2. **Run** (seconds; `--online` adds Crossref/arXiv checks, time-boxed, cached; omit if there is no network):
   ```bash
   python $SKILL_DIR/scripts/cite.py run --manuscript /input/<ms> --library /input/<lib1> [--library ...] \
          --style gbt7714 --online --case-id <case_id> --out /app/output --work /app/work
   ```
   Options: `--marker-style auto|inline|pandoc-sup|html-sup|docx-sup` (default: dominant style in the manuscript),
   `--range-sep -`, `--upper` (GB/T upper-case family names), `--no-auto-move`, `--no-apply-corrections`.
   A library is optional when the manuscript has its own reference list (it is parsed and de-duplicated too).
3. **Judge** – read `/app/work/claim_matrix.md`: one block per citation occurrence (sentence without markers, the
   cited record with title/venue/year/abstract, a lexical support hint) plus sentences that look like claims
   but have no citation. Also read `/app/output/review.md` (merge conflicts, missing/fabricated sources,
   metadata errors, placement suggestions, missing fields). Support scores are hints, not verdicts.
4. **Edit** – copy `/app/work/edits_template.json` to `/app/work/edits.json` and fill it:
   ```json
   {"occurrences": {
      "c4_0": {"verdict": "supported", "note": "LeCun 2015 reports speech + object recognition gains"},
      "c20_1": {"action": "remove", "verdict": "unverifiable", "note": "DOI does not resolve; no registry match"},
      "c8_0": {"verdict": "partial", "move_to": "u8s0", "move_refs": ["M4"], "note": "LSTM belongs to sentence 1"},
      "ins_u8s1": {"verdict": "supported", "note": "auto-moved Transformer citation"}},
    "add_citations": [{"sentence": "text:语言模型的测试损失随模型参数量", "refs": ["L1-2"], "verdict": "supported", "note": "Kaplan 2020"}],
    "record_overrides": {"M5": {"pages": "84-90", "_source": "publisher page / PDF p.1"}},
    "force_merge": [["M3", "L2-4"]], "forbid_merge": [["M1", "M2"]]}
   ```
   - verdict: `supported` | `partial` | `mismatch` | `unverifiable`. Give one for **every** occurrence,
     including `ins_<sentence>` (auto-moved) ones; unjudged occurrences keep the result `partial`.
   - action: `keep` (default) | `remove` | `replace` (`refs`) | `drop_refs` (`refs`); `move_to` a sentence id.
   - refs may be record ids (`M<n>` = n-th entry of the manuscript list, `L<lib>-<k>` = k-th record of the
     lib-th `--library`), original list numbers (`"7"`), or BibTeX keys.
   - sentences: ids `u<unit>s<k>` from claim_matrix, or `"text:<words of the sentence>"` (stable across re-runs).
   - Only add a citation to a record that exists in the inputs; never invent a reference or a field value.
     Put a missing field in `record_overrides` only with a `_source` you actually read (PDF, registry).
5. **Re-run** step 2 with `--edits /app/work/edits.json`. Numbering is recomputed from scratch, the written file is
   re-parsed (`consistency_check`) and `result.json` is rewritten. Repeat 4–5 if needed (each run < 15 s).
6. **Finish** – check `result.json`: `status`, `status_reason`, `consistency_check.ok`, `needs_review`. Fill any
   contract field that `fill_contract` could not map (it maps names containing manuscript/reference/map/merge/
   verif/change/review). Keep `status: partial` when anything needs a human; say why in `status_reason`.

Other commands: `cite.py check --manuscript F` (consistency check of any numbered manuscript, e.g. to test the
original), `cite.py convert --library L --to gbt7714|apa7|bibtex|ris|csl [--dedup] [--online] --out F`
(library-only conversion), `port_edits.py` (carry edits.json over to a changed manuscript / another format).

## What the scripts do

- **Markers** found: `[1]`, `[1,3]`, `[2-5]`, `[1][2]` (joined), `［1］`, `^[1]^`, `<sup>[1]</sup>`,
  `\textsuperscript{}`, docx superscript runs (with or without brackets), `\cite{a,b}`, `[@key]`,
  `(He et al., 2016a; …)`, `He et al. (2016)`, `（何恺明等，2016）`. Markdown links / images are not markers.
- **Sections**: reference list after a heading 参考文献/References/Bibliography (until 附录/Appendix/致谢);
  captions (图/表/Figure/Table, image alt text) and appendix citations are numbered in reading order.
- **Numbering** (GB/T 顺序编码制): first appearance order; duplicates inside one marker collapsed; ranges
  compressed (`[1-3]`, two consecutive numbers stay `[1,2]`); one marker style; uncited list entries removed
  (reported); markers without an entry get a visible placeholder entry `【缺失文献…】` and a review item.
- **Placement**: a cluster at the end of a multi-sentence paragraph is split when a source clearly matches
  an earlier sentence (lexical support ≥0.3 and ≥3× the end position); otherwise a suggestion. Sentences with
  claim cues (研究表明, 已被证明, has been shown, state-of-the-art, numbers …) without a citation are listed.
- **De-dup rules** (logged per pair in `merge_log.json`): D1 same DOI (also zh/en titles of one article),
  D2 same arXiv id, D3 title = translated/alt title, D4 same normalised title + first author, |Δyear|≤2
  (preprint ↔ published), D5 near-identical title (≥0.93) + authors → merged but `needs_review`.
  Guards: G1 same DOI but different titles (DOI error), G2 same title but two publisher DOIs (conference vs
  journal: human choice), G4 same title, years >2 apart (reprint), G3 same authors+year, different title
  (e.g. ResNet vs Identity Mappings) → **not merged**. Canonical = published over preprint, then most complete;
  missing fields filled from the others with `field_provenance`; the longest author list wins; `et al./等` kept.
- **Verification** (`verification.json`): offline field/DOI-prefix-vs-venue/arXiv-year/page/ISBN checks;
  online Crossref DOI lookup, title search (accepted only with title ≥0.9 **and** author overlap **and**
  |Δyear|≤1: Crossref contains junk copies of famous titles), arXiv API, published-version hint for preprints.
  Status per record: `verified`, `verified_with_corrections`, `verified_via_arxiv`, `unverified_no_registry_match`,
  `not_found`, `doi_not_found`, `mismatch`, `unverified_offline`. Corrections (pages, volume, DOI …) are
  applied with source and listed in `changes`; registry author lists shorter than ours are not applied.
- **Formats**: GB/T 7714-2015 ([J] [C]// [M] [D] [R] [S] [P] [EB/OL] [J/OL] for arXiv, ≤3 authors + 等/et al,
  DOI at the end), APA 7 (a/b year suffixes, `&`, DOI URL), BibTeX, RIS, CSL-JSON. Missing required fields are
  reported, never filled with guesses.
- **docx**: run formatting (bold, fonts) kept; markers written as superscript when the manuscript used it;
  the reference list paragraphs reuse the first entry's style; a PDF/PNG preview is rendered when LibreOffice
  is installed. Paragraphs with Word field codes (EndNote/Zotero) are flattened: reported as a warning.

## Outputs (`/app/output`)

| file | content |
|-|-|
| `<stem>_revised.<ext>` | editable manuscript, markers + list rewritten (same format as input) |
| `references_<style>.txt`, `references.bib/.ris/.csl.json` | synced final list in target style + exports |
| `citation_map.json` | every occurrence: unit/sentence id, sentence text, old → new marker, records, numbers, support hint, verdict |
| `renumber_map.json` | old list number → new number (null = removed) |
| `merge_log.json`, `library_dedup.json` | pairwise de-dup decisions with rule + reason; clusters; field provenance; source raw entries |
| `verification.json` | per record status, registry values, corrections, offline issues, network log |
| `manuscript.diff` / `manuscript_changes.md` | line diff (text) / changed paragraphs (docx) |
| `review.md` | human-readable report: status, consistency, items to confirm, changes, verification, occurrences |
| `result.json` | `case_id`, contract fields, `status` (`complete`/`partial`/`failed`), `status_reason`, `summary`, `artifacts`, `references_list`, `changes`, `needs_review`, `consistency_check`, `parse_problems`, `inputs` (sha256), `uncertainty` |

`status` is `complete` only when the consistency check passes, every occurrence has a verdict, no citation was
removed and no blocking item (orphan, fabricated/mismatched source, de-dup conflict) is open.

## Failure handling

| situation | behaviour |
|-|-|
| case.json missing/unreadable | `init` writes `status: failed` with the reason; you may still run on files you find |
| .doc/.pdf/.odt manuscript | `failed` (exit 2) with reason; convert (e.g. `soffice --convert-to docx`) and re-run |
| broken BibTeX entry, RIS without `ER`, unknown format | other entries load; each problem in `parse_problems` |
| no reference list and no library | `failed`, reason given |
| marker number without entry / ambiguous author-year | placeholder entry + `orphan_citation` review item |
| duplicate list labels | reported in `parse_problems`; both entries kept and de-duplicated by content |
| DOI does not resolve / no registry match | `doi_not_found` / `not_found` review items (blocking while cited) |
| network down, rate limit (429) | retry once, then `unverified_offline` with the reason; the run still completes |
| Word field codes in docx | rewritten as text; warning in `status_reason` |

## Limits

- Claim–source matching is lexical (+ a small zh↔en term list); the verdict is yours. Open PDFs or abstracts
  when given; say `unverifiable` when you cannot read the source.
- Author-year resolution needs surname + year to match a record; Chinese names in English records (pinyin)
  are not matched automatically – use edits (`replace`, `force_merge`).
- Crossref has no records for many proceedings (PMLR, ICLR, NeurIPS before 2020), books and Chinese journals:
  these end as `unverified_no_registry_match` / `verified_via_arxiv`, not as fabricated.
- LaTeX: `\cite` keys are rewritten for merged duplicates and a de-duplicated `.bib` is written; numbering is left to BibTeX.
