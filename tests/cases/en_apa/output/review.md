# cite-sync review - case dev-en-apa

status: **success**  
blocking: none  
advisory (does not lower the status): 1 citation(s) with no term overlap between sentence and cited work (heuristic needs_check, not judged by the agent): c2_3; 1 claim sentence(s) without a citation and no fitting record in the inputs: left for the author (not invented)

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 0, "moved_from_paragraph_end": 0, "placement_suggestions": 0, "claims_without_citation": 1, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 6, "references_out": 6, "renumbered_labels": 7, "consistency_ok": null, "order_rule": "author-year"} |
| 去重 dedup | {"records_in": 12, "records_after": 7, "merged_clusters": 4, "rules_used": {"D4": 4, "D2": 1, "D1": 1}, "kept_apart": {}} |
| 格式 format | {"style": "apa7", "entries": 6, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 6} |
| 论断-文献对应 claim match | {"verdicts": {"supported": 4, "partial": 1, "needs_check": 1}, "by_agent": 0, "with_pdf_evidence": 0} |

## Summary
```
{
 "records_in": 12,
 "records_after_dedup": 7,
 "merged_clusters": 4,
 "occurrences": 6,
 "occurrences_out": 6,
 "references_out": 6,
 "orphans": 0,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 6
 },
 "review_items": 2,
 "review_by_type": {
  "claim_without_citation": 1,
  "weak_lexical_support": 1
 },
 "parse_problems": 0,
 "seconds": 0.03
}
```

## Dedup decisions (why records were merged)

| kept | merged records | rules | needs review |
|-|-|-|-|
| L1-4 | M1, L1-4 | D4 | no |
| M4 | M4, L1-2 | D2 | no |
| L1-5 | M5, L1-5 | D1 | no |
| M7 | M6, M7, L1-1 | D4 | no |

Rules: D1 same DOI · D2 same arXiv id · D3 title is the other's translation · D4 same normalised title + first author, year gap <=2 (preprint vs published) · D5 near-identical title + author overlap (confirm). Kept apart: G1 same DOI/different title · G2 same title/two DOIs · G3 same authors+year/different title · G4 reprint (>2 y). Full pair log: merge_log.json.

## Old number -> new number

[1]->removed · [2]->removed · [3]->removed · [4]->removed · [5]->removed · [6]->removed · [7]->removed

## Items that need a human decision

- [advisory] **claim_without_citation** sentence=u2s5 cue=Prior work text=Prior work has shown that dropout prevents overfitting.
- [advisory] **weak_lexical_support** occurrence=c2_3 record=M7 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

## Changes

- {"kind": "merge", "kept": "L1-4", "members": ["M1", "L1-4"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M4", "members": ["M4", "L1-2"], "rules": ["D2"], "needs_review": false}
- {"kind": "merge", "kept": "L1-5", "members": ["M5", "L1-5"], "rules": ["D1"], "needs_review": false}
- {"kind": "merge", "kept": "M7", "members": ["M6", "M7", "L1-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "duplicate_refs_collapsed", "occurrence": "c2_4", "old": "(Ioffe & Szegedy, 2015; Ioffe & Szegedy, 2015)", "reason": "two cited entries are the same work (see merge_log)"}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L1-4 He 2016 Deep Residual Learning for Image Recogniti | unverified_offline |  |  |
| M2 He 2016 Identity mappings in deep residual network | unverified_offline |  |  |
| M3 Ioffe 2015 Batch normalization: Accelerating deep  | unverified_offline |  |  |
| M4 Kaplan 2020 Scaling laws for neural language model | unverified_offline |  |  |
| L1-5 LeCun 2015 Deep learning | unverified_offline |  |  |
| M7 Vaswani 2017 Attention is all you need | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c2_0 | Deep learning has transformed speech and visual recognition. | `(LeCun et al., 2015)` -> `(LeCun et al., 2015)` | L1-5 | {'L1-5': 0.8} | supported |
| c2_1 | Residual networks made models with more than a hundred layers trainabl | `(He et al., 2016a)` -> `(He et al., 2016a)` | L1-4 | {'L1-4': 0.19} | partial |
| c2_2 | Residual networks made models with more than a hundred layers trainabl | `(He et al., 2016b)` -> `(He et al., 2016b)` | M2 | {'M2': 0.57} | supported |
| c2_3 | Residual networks made models with more than a hundred layers trainabl | `Vaswani et al. (2017)` -> `Vaswani et al. (2017)` | M7 | {'M7': 0.0} | needs_check |
| c2_4 | Batch normalization accelerates training by reducing internal covariat | `(Ioffe & Szegedy, 2015; Ioffe & Szegedy, 2015)` -> `(Ioffe & Szegedy, 2015)` | M3 | {'M3': 0.86} | supported |
| c2_5 | Language-model loss falls as a power law in model size, data and compu | `(Kaplan et al., 2020)` -> `(Kaplan et al., 2020)` | M4 | {'M4': 0.38} | supported |
