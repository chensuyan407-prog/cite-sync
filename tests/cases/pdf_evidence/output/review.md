# cite-sync review - case dev-pdf-evidence

status: **success**  
blocking: none  
advisory (does not lower the status): 1 citation(s) with no term overlap between sentence and cited work (heuristic needs_check, not judged by the agent): c8_0; 1 claim sentence(s) without a citation and no fitting record in the inputs: left for the author (not invented)

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 0, "moved_from_paragraph_end": 0, "placement_suggestions": 0, "claims_without_citation": 1, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 5, "references_out": 4, "renumbered_labels": 4, "consistency_ok": true, "order_rule": "first appearance"} |
| 去重 dedup | {"records_in": 4, "records_after": 4, "merged_clusters": 0, "rules_used": {}, "kept_apart": {}} |
| 格式 format | {"style": "gbt7714", "entries": 4, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"verified_by_pdf": 4} |
| 论断-文献对应 claim match | {"verdicts": {"supported": 4, "needs_check": 1}, "by_agent": 0, "with_pdf_evidence": 5} |

## Summary
```
{
 "records_in": 4,
 "records_after_dedup": 4,
 "merged_clusters": 0,
 "occurrences": 5,
 "occurrences_out": 5,
 "references_out": 4,
 "orphans": 0,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 4,
 "verification_status_counts": {
  "verified_by_pdf": 4
 },
 "review_items": 3,
 "review_by_type": {
  "claim_without_citation": 1,
  "weak_lexical_support": 1,
  "possible_miscitation": 1
 },
 "parse_problems": 0,
 "seconds": 1.49
}
```

## Old number -> new number

[1]->[3] · [2]->[1] · [3]->[4] · [4]->[2]

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..4; list entries 4

## Items that need a human decision

- [advisory] **claim_without_citation** sentence=u8s2 cue=has been shown text=It has been shown that dropout reduces overfitting in large networks.
- [advisory] **weak_lexical_support** occurrence=c8_0 record=M2 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match
- [advisory] **possible_miscitation** occurrence=c8_0 records=['M2'] better={'record': 'M3', 'title': 'Scaling laws for neural language models', 'page': 3, 'quote': 'Dataset Size tokens Parameters non-embedding Compute PF-days, non-embedding Test Loss Figure 1 Language modeling performance improves smoothly as we increase the model size, datasetset size, and amoun', 'score': 0.692, 'cited_score': 0.231} msg=the supplied PDF of M3 matches this sentence much better (0.692 vs 0.231) than the cited work

## Changes


## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| M1 Vaswani 2017 Attention is all you need | verified_by_pdf | authors_truncated |  |
| M2 He 2016 Deep residual learning for image recogniti | verified_by_pdf | authors_truncated |  |
| M3 Kaplan 2020 Scaling laws for neural language model | verified_by_pdf | authors_truncated |  |
| M4 Ioffe 2015 Batch normalization: Accelerating deep  | verified_by_pdf |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c4_0 | Residual learning lets networks with more than 100 layers be trained a | `[2]` -> `[1]` | M2 | {'M2': 0.38} | supported |
| c4_1 | Batch normalization normalizes layer inputs over each mini-batch and a | `[4]` -> `[2]` | M4 | {'M4': 0.24} | supported |
| c4_2 | The Transformer relies entirely on attention and dispenses with recurr | `[1]` -> `[3]` | M1 | {'M1': 0.9} | supported |
| c8_0 | The test loss of language models scales as a power law with model size | `[2]` -> `[1]` | M2 | {'M2': 0.0} | needs_check |
| c8_1 | Larger models are significantly more sample-efficient. | `[3]` -> `[4]` | M3 | {'M3': 0.19} | supported |
