# cite-sync review - case None

status: **success**  
blocking: none  
advisory (does not lower the status): 1 detected citation/source issue(s) flagged in needs_review: orphan_citation; 1 citation(s) point to an unverified or missing source (flagged in needs_review): c4_0; 1 citation(s) with no term overlap between sentence and cited work (heuristic needs_check, not judged by the agent): c2_0

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 0, "moved_from_paragraph_end": 0, "placement_suggestions": 0, "claims_without_citation": 0, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 4, "references_out": 4, "renumbered_labels": 0, "consistency_ok": null, "order_rule": "author-year"} |
| 去重 dedup | {"records_in": 6, "records_after": 5, "merged_clusters": 1, "rules_used": {"D4": 1}, "kept_apart": {}} |
| 格式 format | {"style": "gbt7714", "entries": 4, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 3} |
| 论断-文献对应 claim match | {"verdicts": {"needs_check": 1, "supported": 2, "unverifiable": 1}, "by_agent": 0, "with_pdf_evidence": 0} |

## Summary
```
{
 "records_in": 6,
 "records_after_dedup": 5,
 "merged_clusters": 1,
 "occurrences": 4,
 "occurrences_out": 4,
 "references_out": 4,
 "orphans": 1,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 3
 },
 "review_items": 2,
 "review_by_type": {
  "orphan_citation": 1,
  "weak_lexical_support": 1
 },
 "parse_problems": 1,
 "seconds": 0.02
}
```

## Dedup decisions (why records were merged)

| kept | merged records | rules | needs review |
|-|-|-|-|
| L1-1 | L1-1, L1-6 | D4 | no |

Rules: D1 same DOI · D2 same arXiv id · D3 title is the other's translation · D4 same normalised title + first author, year gap <=2 (preprint vs published) · D5 near-identical title + author overlap (confirm). Kept apart: G1 same DOI/different title · G2 same title/two DOIs · G3 same authors+year/different title · G4 reprint (>2 y). Full pair log: merge_log.json.

## Items that need a human decision

- [advisory] **orphan_citation** marker=nokey2020 occurrences=['c4_0'] msg=in-text citation has no reference entry
- [advisory] **weak_lexical_support** occurrence=c2_0 record=L1-1 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

## Changes

- {"kind": "merge", "kept": "L1-1", "members": ["L1-1", "L1-6"], "rules": ["D4"], "needs_review": false}
- {"kind": "duplicate_refs_collapsed", "occurrence": "c2_0", "old": "\\cite{vaswani2017attention,vaswani2017arxiv}", "reason": "two cited entries are the same work (see merge_log)"}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L1-1 Vaswani 2017 Attention is all you need | unverified_offline |  |  |
| L1-4 He 2016 Deep Residual Learning for Image Recogniti | unverified_offline |  |  |
| L1-5 LeCun 2015 Deep learning | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c2_0 | Attention-only models were introduced in. | `\cite{vaswani2017attention,vaswani2017arxiv}` -> `\cite{vaswani2017attention}` | L1-1 | {'L1-1': 0.0} | needs_check |
| c3_0 | Very deep residual networks and the deep-learning review are standard  | `\citep{he2016deep}` -> `\citep{he2016deep}` | L1-4 | {'L1-4': 0.38} | supported |
| c3_1 | Very deep residual networks and the deep-learning review are standard  | `\cite{lecun2015deep}` -> `\cite{lecun2015deep}` | L1-5 | {'L1-5': 0.4} | supported |
| c4_0 | A missing key should be reported. | `\cite{nokey2020}` -> `\cite{nokey2020}` | MISSING-nokey2020 | {'MISSING-nokey2020': 0.0} | unverifiable |
