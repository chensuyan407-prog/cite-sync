# cite-sync review - case holdout-gnn

status: **partial**  
reasons: 1 blocking item(s) need human confirmation; 9 citation occurrence(s) without a claim-source verdict (fill edits.occurrences.*.verdict)

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
 "verified": 2,
 "verification_status_counts": {
  "unverified_no_registry_match": 4,
  "verified_via_arxiv": 1,
  "verified": 1
 },
 "review_items": 9,
 "review_by_type": {
  "orphan_citation": 1,
  "source_unconfirmed": 4,
  "uncited_entry_removed": 1,
  "weak_lexical_support": 3
 },
 "parse_problems": 0,
 "seconds": 0.03
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..7; list entries 7

## Items that need a human decision

- **orphan_citation** marker=9 occurrences=['c12_0'] msg=in-text citation has no reference entry
- **source_unconfirmed** record=L2-1 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **source_unconfirmed** record=M2 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **source_unconfirmed** record=M5 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **source_unconfirmed** record=M6 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **uncited_entry_removed** record=M8 msg=reference-list entry never cited in the text; removed from the list: Hamilton 2017 Inductive representation learning on large graphs
- **weak_lexical_support** occurrence=c8_2 record=M7 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match
- **weak_lexical_support** occurrence=c8_2 record=L1-1 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match
- **weak_lexical_support** occurrence=c10_0 record=M7 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

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
| L2-1 Veličković 2018 Graph Attention Networks | unverified_no_registry_match |  |  |
| M2 Brown 2020 Language models are few-shot learners | unverified_no_registry_match | authors_truncated |  |
| M7 Kipf 2017 Semi-supervised classification with grap | verified_via_arxiv |  |  |
| L1-1 Devlin 2019 BERT: Pre-training of Deep Bidirection | verified |  |  |
| M5 Kingma 2015 Adam: A method for stochastic optimiza | unverified_no_registry_match |  |  |
| M6 Srivastava 2014 Dropout: a simple way to prevent n | unverified_no_registry_match | authors_truncated |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict | evidence / review note |
|-|-|-|-|-|-|-|
| c4_0 | 图卷积网络将卷积运算推广到图结构数据。 | `^[3]^` -> `^[1]^` | M7 | {'M7': 0.19} | - | - |
| c4_1 | 图注意力网络为邻居节点分配不同的注意力权重。 | `^[1]^` -> `^[2]^` | L2-1 | {'L2-1': 0.283} | - | - |
| c4_2 | 在自然语言处理领域，GPT-3 展示了大规模语言模型的少样本学习能力，而 BERT 采用掩码语言模型进行双向预训练。 | `^[2]^` -> `^[3]^` | M2 | {'M2': 0.9} | - | - |
| c4_3 | 在自然语言处理领域，GPT-3 展示了大规模语言模型的少样本学习能力，而 BERT 采用掩码语言模型进行双向预训练。 | `^[4]^` -> `^[4]^` | L1-1 | {'L1-1': 0.6} | - | - |
| c8_0 | 本文采用的优化器为 Adam，并在训练中使用 Dropout 防止过拟合。 | `^[5]^` -> `^[5]^` | M5 | {'M5': 0.675} | - | - |
| c8_1 | 本文采用的优化器为 Adam，并在训练中使用 Dropout 防止过拟合。 | `^[6]^` -> `^[6]^` | M6 | {'M6': 0.3} | - | - |
| c8_2 | 相关的图表示学习方法可参见文献。 | `^[3-5]^` -> `^[1,4]^` | M7, L1-1 | {'M7': 0.0, 'L1-1': 0.0} | - | - |
| c10_0 | 实验表明，模型在 Cora 数据集上的准确率达到 83.0%。 | `^[7]^` -> `^[1]^` | M7 | {'M7': 0.0} | - | - |
| c12_0 | 我们进一步参考了 Transformer 架构。 | `^[9]^` -> `^[7]^` | MISSING-9 | {'MISSING-9': 0.0} | - | - |
