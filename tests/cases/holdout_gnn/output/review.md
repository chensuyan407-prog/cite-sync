# cite-sync review - case holdout-gnn

status: **success**  
blocking: none  
advisory (does not lower the status): 1 detected citation/source issue(s) flagged in needs_review: orphan_citation; 1 citation(s) point to an unverified or missing source (flagged in needs_review): c12_0; 2 citation(s) with no term overlap between sentence and cited work (heuristic needs_check, not judged by the agent): c8_2, c10_0

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 0, "moved_from_paragraph_end": 1, "placement_suggestions": 0, "claims_without_citation": 0, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 9, "references_out": 7, "renumbered_labels": 5, "consistency_ok": true, "order_rule": "first appearance"} |
| 去重 dedup | {"records_in": 11, "records_after": 7, "merged_clusters": 4, "rules_used": {"D4": 4}, "kept_apart": {}} |
| 格式 format | {"style": "gbt7714", "entries": 7, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 6} |
| 论断-文献对应 claim match | {"verdicts": {"supported": 5, "partial": 1, "needs_check": 2, "unverifiable": 1}, "by_agent": 0, "with_pdf_evidence": 0} |

## Summary
```
{
 "records_in": 11,
 "records_after_dedup": 7,
 "merged_clusters": 4,
 "occurrences": 9,
 "occurrences_out": 9,
 "references_out": 7,
 "orphans": 1,
 "uncited_removed": 1,
 "auto_moves": 1,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 6
 },
 "review_items": 5,
 "review_by_type": {
  "orphan_citation": 1,
  "uncited_entry_removed": 1,
  "weak_lexical_support": 3
 },
 "parse_problems": 0,
 "seconds": 0.03
}
```

## Dedup decisions (why records were merged)

| kept | merged records | rules | needs review |
|-|-|-|-|
| L2-1 | M1, L2-1 | D4 | no |
| M7 | M3, M7 | D4 | no |
| L1-1 | M4, L1-1 | D4 | no |
| M8 | M8, L1-2 | D4 | no |

Rules: D1 same DOI · D2 same arXiv id · D3 title is the other's translation · D4 same normalised title + first author, year gap <=2 (preprint vs published) · D5 near-identical title + author overlap (confirm). Kept apart: G1 same DOI/different title · G2 same title/two DOIs · G3 same authors+year/different title · G4 reprint (>2 y). Full pair log: merge_log.json.

## Old number -> new number

[1]->[2] · [2]->[3] · [3]->[1] · [4]->[4] · [5]->[5] · [6]->[6] · [7]->[1] · [8]->removed

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..7; list entries 7

## Items that need a human decision

- [advisory] **orphan_citation** marker=9 occurrences=['c12_0'] msg=in-text citation has no reference entry
- [advisory] **uncited_entry_removed** record=M8 msg=reference-list entry never cited in the text; removed from the list: Hamilton 2017 Inductive representation learning on large graphs
- [advisory] **weak_lexical_support** occurrence=c8_2 record=M7 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match
- [advisory] **weak_lexical_support** occurrence=c8_2 record=L1-1 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match
- [advisory] **weak_lexical_support** occurrence=c10_0 record=M7 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

## Changes

- {"kind": "merge", "kept": "L2-1", "members": ["M1", "L2-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M7", "members": ["M3", "M7"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L1-1", "members": ["M4", "L1-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M8", "members": ["M8", "L1-2"], "rules": ["D4"], "needs_review": false}
- {"kind": "citation_moved", "occurrence": "c8_2", "record": "M5", "from_sentence": "u8s1", "to_sentence": "u8s0", "reason": "lexical support 0.0 at paragraph end vs 0.675 at target sentence", "needs_review": true}
- {"kind": "move_target_already_cites", "sentence": "u8s0", "records": ["M5"], "reason": "target sentence already cites this work; not cited a second time"}
- {"kind": "entry_removed_uncited", "record": "M8", "members": ["M8", "L1-2"]}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L2-1 Veličković 2018 Graph Attention Networks | unverified_offline |  |  |
| M2 Brown 2020 Language models are few-shot learners | unverified_offline | authors_truncated |  |
| M7 Kipf 2017 Semi-supervised classification with grap | unverified_offline |  |  |
| L1-1 Devlin 2019 BERT: Pre-training of Deep Bidirection | unverified_offline |  |  |
| M5 Kingma 2015 Adam: A method for stochastic optimiza | unverified_offline |  |  |
| M6 Srivastava 2014 Dropout: a simple way to prevent n | unverified_offline | authors_truncated |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c4_0 | 图卷积网络将卷积运算推广到图结构数据。 | `^[3]^` -> `^[1]^` | M7 | {'M7': 0.38} | supported |
| c4_1 | 图注意力网络为邻居节点分配不同的注意力权重。 | `^[1]^` -> `^[2]^` | L2-1 | {'L2-1': 0.283} | partial |
| c4_2 | 在自然语言处理领域，GPT-3 展示了大规模语言模型的少样本学习能力，而 BERT 采用掩码语言模型进行双向预训练。 | `^[2]^` -> `^[3]^` | M2 | {'M2': 0.9} | supported |
| c4_3 | 在自然语言处理领域，GPT-3 展示了大规模语言模型的少样本学习能力，而 BERT 采用掩码语言模型进行双向预训练。 | `^[4]^` -> `^[4]^` | L1-1 | {'L1-1': 0.6} | supported |
| c8_0 | 本文采用的优化器为 Adam，并在训练中使用 Dropout 防止过拟合。 | `^[5]^` -> `^[5]^` | M5 | {'M5': 0.675} | supported |
| c8_1 | 本文采用的优化器为 Adam，并在训练中使用 Dropout 防止过拟合。 | `^[6]^` -> `^[6]^` | M6 | {'M6': 0.3} | supported |
| c8_2 | 相关的图表示学习方法可参见文献。 | `^[3-5]^` -> `^[1,4]^` | M7, L1-1 | {'M7': 0.0, 'L1-1': 0.0} | needs_check |
| c10_0 | 实验表明，模型在 Cora 数据集上的准确率达到 83.0%。 | `^[7]^` -> `^[1]^` | M7 | {'M7': 0.0} | needs_check |
| c12_0 | 我们进一步参考了 Transformer 架构。 | `^[9]^` -> `^[7]^` | MISSING-9 | {'MISSING-9': 0.0} | unverifiable |
