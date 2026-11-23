# cite-sync 0.1.0 — method, files, mapping tables, limits

Agent Skill for **写作04｜参考文献与引用管理**. Sub-problem chosen: keep the **in-text citations and the
reference list in sync** through insertion, deletion, re-ordering and de-duplication, with an explainable
de-dup decision per pair, registry checks per record and a judged claim–source verdict per citation. Every
step is written to a ledger, and the finished file is re-parsed to prove the numbering is consistent.
It is not a reference manager. It works on one manuscript plus the libraries handed to it.

## Files

| path | role |
|---|---|
| `SKILL.md` | agent instructions (workflow, edits format, outputs, failure handling) |
| `scripts/cite.py` | CLI: `init`, `run`, `check`, `convert`; numbering, placement, edits, outputs, result.json |
| `scripts/cite_doc.py` | manuscript model for .md/.txt/.tex/.docx: sections, captions, sentence ids, marker grammar, rewriting (docx run-level) |
| `scripts/cite_parse.py` | BibTeX, RIS, EndNote/Refer (CNKI EndNote export), NoteExpress, CSL-JSON, free-text GB/T / APA / Vancouver lists |
| `scripts/cite_dedup.py` | pairwise rules D1–D5, guards G1–G4, H1/H2 explicit edits; clusters, canonical choice, field provenance |
| `scripts/cite_format.py` | GB/T 7714-2015, APA 7, BibTeX, RIS, CSL-JSON renderers; marker rendering and range compression |
| `scripts/cite_verify.py` | offline checks, Crossref/arXiv client (cache, budget, retry), support hints, claim cues |
| `scripts/cite_common.py` | normalisation, similarity, names, DOI/arXiv ids, IO |
| `scripts/port_edits.py` | carry an edits.json across re-runs whose occurrence ids changed |
| `examples/` | minimal input + `minimal_example.md` (calls and an excerpt of the output, marked as an example) |
| `requirements.txt` | none for text formats; `python-docx` for .docx; optional PyMuPDF + LibreOffice for previews |

Dependencies: Python ≥ 3.9 standard library. `python-docx >= 0.8` (tested 1.2.0) only for .docx.
Network is optional (Crossref REST `api.crossref.org`, arXiv `export.arxiv.org`). Responses are cached in
`<work>/net_cache.json`. Budget defaults: 150 s and 80 requests (`--net-budget`), timeout 8 s, one retry on 429/5xx.

## Pipeline (`cite.py run`)

1. Load the manuscript and split it into units (lines or docx paragraphs). Find the reference section, captions and appendix.
2. Detect markers (grammar in SKILL.md) and split sentences, with markers masked so `et al.`/`Fig.` do not split. A marker
   after the full stop belongs to the sentence before it. Ids: unit `u<i>`, sentence `u<i>s<k>`, occurrence `c<i>_<j>`.
3. Parse the manuscript list (`M<label>`) and every library (`L<lib>-<k>`). Problems are collected and never fatal.
4. De-duplicate (below). Resolve each marker to cluster ids: number → list label, key → bibkey, author-year →
   surname + year (+a/b suffix). A marker that resolves to nothing gets a placeholder record `MISSING-<x>`.
5. Verify the cited records (offline always, online with `--online`) and apply registry corrections with their source.
6. Placement: support hints per (sentence, record). Paragraph-end clusters are split when the evidence is clear.
7. Apply edits (remove / replace / drop_refs / move_to / add_citations / record_overrides / force|forbid_merge).
8. Number by first appearance over body, captions and appendix in reading order. Rewrite the markers in one style
   and render the list in the target style. Write the files.
9. Re-parse the written manuscript (`check_manuscript`): order of first appearance, 1..N continuous, list size = N,
   no number without an entry, no uncited entry, no duplicate entries or DOIs, one marker style.
10. Write `result.json`, `review.md`, `claim_matrix.md` and `edits_template.json`.

## De-dup rules (`merge_log.json` keeps one line per decided pair)

| rule | condition | decision |
|-|-|-|
| G1 | same DOI, same language, title similarity < 0.6 | not merged; conflict (one DOI is wrong) |
| D1 | same DOI (case-insensitive); also when the titles are zh vs en | merge |
| D2 | same arXiv id (version ignored) | merge |
| D3 | title of one = `title_alt` (translated title) of the other; years ≤1 apart | merge |
| G2 | identical title, two different non-arXiv DOIs | not merged; human picks the version |
| D4 | identical normalised title, first author equal/unknown or overlap ≥0.5, years ≤2 apart | merge (preprint ↔ published) |
| D5 | title similarity ≥0.93, author overlap ≥0.5 or unknown, years ≤2 apart | merge, `needs_review` |
| G4 | identical title, years >2 apart | not merged (reprint, e.g. NIPS 2012 vs CACM 2017) |
| G3 | same author set, same year, different title (sim ≥0.5) | not merged, logged as a near miss |
| H1/H2 | `force_merge` / `forbid_merge` edit | as given; a forbidden pair also blocks transitive joins |

Canonical record: published before preprint, then most filled fields. Missing fields are filled from other members
(`field_provenance`), the longest author list wins, `authors_truncated` is kept when no member lists more names,
and the arXiv id of a merged preprint is kept.

## Format mapping (excerpt)

| type | GB/T 7714-2015 | APA 7 | BibTeX | RIS |
|-|-|-|-|-|
| journal article | `A, B, C, 等. 题名[J]. 刊名, 年, 卷(期): 页. DOI:x.` | `A., B., & C. (Y). Title. Journal, V(I), p–p. https://doi.org/x` | `@article` | `JOUR` |
| conference | `…[C]//会议录. 地: 出版者, 年: 页.` | `… In Proceedings (pp. p–p). Publisher.` | `@inproceedings` | `CPAPER` |
| book | `…[M]. 版. 地: 出版者, 年.` | `… Title (ed.). Publisher.` | `@book` | `BOOK` |
| thesis / report / standard | `[D]` / `[R]` / `[S]` | — | `@phdthesis` / `@techreport` | `THES` / `RPRT` / `STAND` |
| arXiv preprint | `…[J/OL]. arXiv preprint arXiv:id, 年. URL.` | `… (arXiv:id). arXiv. https://doi.org/10.48550/arXiv.id` | `@misc` + `eprint` | `UNPB` |
| web page / dataset | `[EB/OL]` / `[DB/OL]` + (date)[引用日期] + URL | — | `@online` | `ELEC` / `DATA` |

Input field mapping: BibTeX `journal|journaltitle|booktitle → container`, `number|issue → issue`, `school|institution|publisher → publisher`,
`eprint+archiveprefix=arXiv → arxiv`. RIS `TI|T1`, `AU|A1`, `T2|JO|JF|BT`, `PY|Y1|DA`, `SP+EP`, `DO`, `TT → title_alt`.
EndNote `%A %T %J|%B %D %V %N %P %R(DOI) %I %C %Q(translated title)`. CNKI exports `%A 甲;乙;丙`.
NoteExpress `{Author} {Title} {Secondary Title} {Translated Title}`. CSL-JSON standard keys, `original-title → title_alt`.

## Evaluation (author's cases, `python src/reproduce.py` in the bundle)

There are 3 dev cases: a Chinese GB/T markdown review with 12 cited works from 3 libraries (bib + RIS + CNKI enw),
the same manuscript as .docx with superscript markers, and an English APA note. There is 1 held-out case written
after a code freeze (CSL-JSON + NoteExpress, pandoc superscripts, a range marker, an orphan, a preprint and published
pair). All references are real and checkable. The planted defects are scored on the written files and compared with
B0 (untouched) and B1 (a regex that renumbers by first appearance and reorders the list, nothing else).
See `execution/results/metrics.json`. A failure found after the freeze is reported separately, not hidden.

## Known failure modes (seen while building)

- Crossref title search returns junk copies of famous papers (e.g. a 2025 record titled "Attention Is All You Need"
  whose authors match). A title match alone used to overwrite the year and DOI, so search hits now need a year match too.
- A Crossref 429 response was cached as "search failed". Errors are no longer cached and are retried once.
- Crossref lists only the first author for some Chinese journals (Hans `10.12677`). The record's longer list is kept.
- A source moved out of a paragraph-end range was glued onto the next marker in a sentence that already cited it.
  A move into a sentence that already cites the work is now dropped and logged.
- An unnumbered APA list used to be read as one long entry. It is now read one entry per line.
- The JMLR Dropout paper (JMLR registers no DOIs) was reported as "possibly fabricated" because Crossref has no record of it.
  Absence from Crossref now blocks only for venues whose publishers register every article (Nature, Science, IEEE, ACM,
  Elsevier, Springer, ...). Elsewhere it is `unverified_no_registry_match`.

## Limits

Lexical support is a hint. It cannot see that "83.0% on Cora" is GAT's number, not GCN's, so the agent's verdict
(and a PDF, when available) is needed. Matching pinyin to Chinese names is not done. Word field codes are flattened.
LaTeX numbering is left to BibTeX. No CSL engine: GB/T and APA are hand-written renderers for the common types.

Maintainer: chensuyan407-prog. MIT licence. Issues and new failure cases are welcome.
