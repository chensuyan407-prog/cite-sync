# cite-sync review - case None

status: **success**  
blocking: none  
advisory (does not lower the status): 1 detected citation/source issue(s) flagged in needs_review: orphan_citation; 1 citation(s) point to an unverified or missing source (flagged in needs_review): c2_2; 1 citation(s) with no term overlap between sentence and cited work (heuristic needs_check, not judged by the agent): c2_1

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 0, "moved_from_paragraph_end": 0, "placement_suggestions": 0, "claims_without_citation": 0, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 3, "references_out": 3, "renumbered_labels": 2, "consistency_ok": true, "order_rule": "first appearance"} |
| 去重 dedup | {"records_in": 3, "records_after": 2, "merged_clusters": 1, "rules_used": {"D4": 1}, "kept_apart": {}} |
| 格式 format | {"style": "gbt7714", "entries": 3, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 2} |
| 论断-文献对应 claim match | {"verdicts": {"supported": 1, "needs_check": 1, "unverifiable": 1}, "by_agent": 0, "with_pdf_evidence": 0} |

## Summary
```
{
 "records_in": 3,
 "records_after_dedup": 2,
 "merged_clusters": 1,
 "occurrences": 3,
 "occurrences_out": 3,
 "references_out": 3,
 "orphans": 1,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 2
 },
 "review_items": 2,
 "review_by_type": {
  "orphan_citation": 1,
  "weak_lexical_support": 1
 },
 "parse_problems": 1,
 "seconds": 0.01
}
```

## Dedup decisions (why records were merged)

| kept | merged records | rules | needs review |
|-|-|-|-|
| M2 | M2, M2_3 | D4 | no |

Rules: D1 same DOI · D2 same arXiv id · D3 title is the other's translation · D4 same normalised title + first author, year gap <=2 (preprint vs published) · D5 near-identical title + author overlap (confirm). Kept apart: G1 same DOI/different title · G2 same title/two DOIs · G3 same authors+year/different title · G4 reprint (>2 y). Full pair log: merge_log.json.

## Old number -> new number

[1]->[2] · [2]->[1]

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..3; list entries 3

## Items that need a human decision

- [advisory] **orphan_citation** marker=7 occurrences=['c2_2'] msg=in-text citation has no reference entry
- [advisory] **weak_lexical_support** occurrence=c2_1 record=M2 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

## Changes

- {"kind": "merge", "kept": "M2", "members": ["M2", "M2_3"], "rules": ["D4"], "needs_review": false}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| M1 Hochreiter 1997 Long short-term memory | unverified_offline |  |  |
| M2 LeCun 2015 Deep learning | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c2_0 | 深度学习综述见文献。 | `[2]` -> `[1]` | M2 | {'M2': 0.8} | supported |
| c2_1 | 长短期记忆网络见。 | `[1-2]` -> `[1,2]` | M1, M2 | {'M1': 0.85, 'M2': 0.0} | needs_check |
| c2_2 | 另见。 | `[7]` -> `[3]` | MISSING-7 | {'MISSING-7': 0.0} | unverifiable |
