# cite-sync review - case libonly

status: **success**  
blocking: none  
advisory (does not lower the status): none

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 0, "moved_from_paragraph_end": 0, "placement_suggestions": 0, "claims_without_citation": 0, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 0, "references_out": 8, "renumbered_labels": 0, "consistency_ok": null, "order_rule": "first appearance"} |
| 去重 dedup | {"records_in": 9, "records_after": 8, "merged_clusters": 1, "rules_used": {"D1": 1}, "kept_apart": {}} |
| 格式 format | {"style": "gbt7714", "entries": 8, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 8} |
| 论断-文献对应 claim match | {"verdicts": {}, "by_agent": 0, "with_pdf_evidence": 0} |

## Summary
```
{
 "records_in": 9,
 "records_after_dedup": 8,
 "merged_clusters": 1,
 "occurrences": 0,
 "occurrences_out": 0,
 "references_out": 8,
 "orphans": 0,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 8
 },
 "review_items": 0,
 "review_by_type": {},
 "parse_problems": 0,
 "seconds": 0.01
}
```

## Dedup decisions (why records were merged)

| kept | merged records | rules | needs review |
|-|-|-|-|
| L1-1 | L1-1, L3-3 | D1 | no |

Rules: D1 same DOI · D2 same arXiv id · D3 title is the other's translation · D4 same normalised title + first author, year gap <=2 (preprint vs published) · D5 near-identical title + author overlap (confirm). Kept apart: G1 same DOI/different title · G2 same title/two DOIs · G3 same authors+year/different title · G4 reprint (>2 y). Full pair log: merge_log.json.

## Items that need a human decision


## Changes

- {"kind": "merge", "kept": "L1-1", "members": ["L1-1", "L3-3"], "rules": ["D1"], "needs_review": false}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L1-1 袁铭阳 2020 卷积神经网络池化方法综述 | unverified_offline |  |  |
| L2-1 Vaswani 2017 Attention is all you need | unverified_offline |  |  |
| L2-2 Kaplan 2020 Scaling laws for neural language model | unverified_offline |  |  |
| L2-3 Krizhevsky 2012 ImageNet classification with deep  | unverified_offline |  |  |
| L2-4 He 2016 Deep Residual Learning for Image Recogniti | unverified_offline |  |  |
| L2-5 LeCun 2015 Deep learning | unverified_offline |  |  |
| L3-1 Devlin 2018 BERT: Pre-training of Deep Bidirection | unverified_offline |  |  |
| L3-2 Jumper 2021 Highly accurate protein structure pred | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
