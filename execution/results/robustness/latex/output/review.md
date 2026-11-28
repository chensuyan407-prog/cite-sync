# cite-sync review - case None

status: **partial**  
reasons: 1 blocking item(s) need human confirmation; 4 citation occurrence(s) without a claim-source verdict (fill edits.occurrences.*.verdict); sources not checked online (offline run)

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

## Items that need a human decision

- **orphan_citation** marker=nokey2020 occurrences=['c4_0'] msg=in-text citation has no reference entry
- **weak_lexical_support** occurrence=c2_0 record=L1-1 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

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

| occ | sentence | marker old -> new | records | support | verdict | evidence / review note |
|-|-|-|-|-|-|-|
| c2_0 | Attention-only models were introduced in . | `\cite{vaswani2017attention,vaswani2017arxiv}` -> `\cite{vaswani2017attention}` | L1-1 | {'L1-1': 0.0} | - | - |
| c3_0 | Very deep residual networks and the deep-learning review are standard  | `\citep{he2016deep}` -> `\citep{he2016deep}` | L1-4 | {'L1-4': 0.38} | - | - |
| c3_1 | Very deep residual networks and the deep-learning review are standard  | `\cite{lecun2015deep}` -> `\cite{lecun2015deep}` | L1-5 | {'L1-5': 0.4} | - | - |
| c4_0 | A missing key should be reported. | `\cite{nokey2020}` -> `\cite{nokey2020}` | MISSING-nokey2020 | {'MISSING-nokey2020': 0.0} | - | - |
