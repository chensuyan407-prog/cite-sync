# cite-sync review - case None

status: **success**  
blocking: none  
advisory (does not lower the status): 1 claim sentence(s) have candidate library record(s) suggested in review.md/brief.md

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 2, "moved_from_paragraph_end": 2, "placement_suggestions": 0, "claims_without_citation": 1, "claims_with_library_candidate": 1} |
| 编号同步 renumbering | {"markers": 13, "references_out": 12, "renumbered_labels": 12, "consistency_ok": true, "order_rule": "first appearance"} |
| 去重 dedup | {"records_in": 22, "records_after": 16, "merged_clusters": 6, "rules_used": {"D4": 6}, "kept_apart": {"G4": 1}} |
| 格式 format | {"style": "gbt7714", "entries": 12, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 12} |
| 论断-文献对应 claim match | {"verdicts": {"supported": 12, "partial": 1}, "by_agent": 0, "with_pdf_evidence": 0} |

## Summary
```
{
 "records_in": 22,
 "records_after_dedup": 16,
 "merged_clusters": 6,
 "occurrences": 11,
 "occurrences_out": 13,
 "references_out": 12,
 "orphans": 0,
 "uncited_removed": 1,
 "auto_moves": 2,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 12
 },
 "review_items": 3,
 "review_by_type": {
  "uncited_entry_removed": 1,
  "claim_without_citation": 1,
  "caption_citation": 1
 },
 "parse_problems": 2,
 "seconds": 0.05
}
```

## Dedup decisions (why records were merged)

| kept | merged records | rules | needs review |
|-|-|-|-|
| L1-4 | M1, L1-4 | D4 | no |
| L1-5 | M3, L1-5 | D4 | no |
| M6 | M6, M8 | D4 | no |
| L1-1 | M7, L1-1 | D4 | no |
| M9 | M9, L2-1 | D4 | no |
| L2-2 | M11, L2-2 | D4 | no |

Rules: D1 same DOI · D2 same arXiv id · D3 title is the other's translation · D4 same normalised title + first author, year gap <=2 (preprint vs published) · D5 near-identical title + author overlap (confirm). Kept apart: G1 same DOI/different title · G2 same title/two DOIs · G3 same authors+year/different title · G4 reprint (>2 y). Full pair log: merge_log.json.

## Old number -> new number

[1]->[3] · [2]->[4] · [3]->[1] · [4]->[5] · [5]->[2] · [6]->[8] · [7]->[6] · [8]->[8] · [9]->[7] · [10]->[9] · [11]->[11] · [12]->[10] · [13]->removed · [14]->[12]

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..12; list entries 12

## Items that need a human decision

- [advisory] **uncited_entry_removed** record=M13 msg=reference-list entry never cited in the text; removed from the list: Srivastava 2014 Dropout: a simple way to prevent neural networks from overfi
- [advisory] **claim_without_citation** sentence=u10s0 cue=已有研究 text=已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训练算力呈幂律下降。 suggest=[{'record': 'L1-2', 'score': 0.76, 'title': 'Scaling laws for neural language models', 'year': '2020', 'already_cited': False}] edit={'sentence': 'text:已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训', 'refs': ['L1-2'], 'verdict': 'supported', 'note': '<why this source supports the sentence>'}
- [advisory] **caption_citation** occurrence=c16_0 msg=citation sits in a figure/table caption; check that the supported claim is in the caption, not in the body text

## Changes

- {"kind": "merge", "kept": "L1-4", "members": ["M1", "L1-4"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L1-5", "members": ["M3", "L1-5"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M6", "members": ["M6", "M8"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L1-1", "members": ["M7", "L1-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M9", "members": ["M9", "L2-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L2-2", "members": ["M11", "L2-2"], "rules": ["D4"], "needs_review": false}
- {"kind": "duplicate_refs_collapsed", "occurrence": "c14_0", "old": "[6,8]", "reason": "two cited entries are the same work (see merge_log)"}
- {"kind": "citation_moved", "occurrence": "c8_0", "record": "M4", "from_sentence": "u8s2", "to_sentence": "u8s0", "reason": "lexical support 0.0 at paragraph end vs 0.85 at target sentence", "needs_review": true}
- {"kind": "citation_moved", "occurrence": "c8_0", "record": "L1-1", "from_sentence": "u8s2", "to_sentence": "u8s1", "reason": "lexical support 0.0 at paragraph end vs 0.9 at target sentence", "needs_review": true}
- {"kind": "markers_joined", "occurrence": "c8_0", "old": "[4][7][9]", "new": "[7]"}
- {"kind": "marker_style_unified", "occurrence": "c14_1", "old": "<sup>[10]</sup>", "new": "[9]", "reason": "html-sup -> dominant style inline"}
- {"kind": "entry_removed_uncited", "record": "M13", "members": ["M13"]}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L1-4 He 2016 Deep Residual Learning for Image Recogniti | unverified_offline |  |  |
| M2 He 2016 Identity mappings in deep residual network | unverified_offline | authors_truncated |  |
| L1-5 LeCun 2015 Deep learning | unverified_offline |  |  |
| M4 Hochreiter 1997 Long short-term memory | unverified_offline |  |  |
| M5 Krizhevsky 2017 ImageNet classification with deep  | unverified_offline |  |  |
| M6 Ioffe 2015 Batch normalization: Accelerating deep  | unverified_offline |  |  |
| L1-1 Vaswani 2017 Attention is all you need | unverified_offline |  |  |
| M9 Devlin 2019 BERT: Pre-training of deep bidirection | unverified_offline |  |  |
| M10 Kingma 2014 Adam: A method for stochastic optimiza | unverified_offline |  |  |
| L2-2 Jumper 2021 Highly accurate protein structure pred | unverified_offline | authors_truncated |  |
| M12 袁铭阳 2020 卷积神经网络池化方法综述 | unverified_offline | authors_truncated |  |
| M14 Smith 2019 Universal scaling of residual attention | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c4_0 | 深度学习通过多层表示学习显著提升了语音识别、视觉目标识别等任务的性能。 | `[3]` -> `[1]` | L1-5 | {'L1-5': 0.8} | supported |
| c4_1 | 卷积神经网络在 ImageNet 图像分类竞赛中取得突破，大幅降低了 top-5 错误率。 | `[5]` -> `[2]` | M5 | {'M5': 0.833} | supported |
| c4_2 | 随后，残差学习框架使得训练上百层的网络成为可能；同一团队又分析了恒等映射在残差单元中的作用。 | `[1]` -> `[3]` | L1-4 | {'L1-4': 0.57} | supported |
| c4_3 | 随后，残差学习框架使得训练上百层的网络成为可能；同一团队又分析了恒等映射在残差单元中的作用。 | `[2]` -> `[4]` | M2 | {'M2': 0.76} | supported |
| ins_u8s0 | 长短期记忆网络通过门控机制缓解了循环网络的梯度消失问题。 | `` -> `[5]` | M4 | {'M4': 0.85} | supported |
| ins_u8s1 | Transformer 完全基于注意力机制，在机器翻译任务上取得了当时最好的结果。 | `` -> `[6]` | L1-1 | {'L1-1': 0.9} | supported |
| c8_0 | BERT 通过双向预训练显著提升了多项语言理解任务的表现。 | `[4][7][9]` -> `[7]` | M9 | {'M9': 0.75} | supported |
| c14_0 | 批归一化通过减少内部协变量偏移加速了深层网络训练。 | `[6,8]` -> `[8]` | M6 | {'M6': 0.79} | supported |
| c14_1 | Adam 优化器被广泛用于训练上述模型。 | `<sup>[10]</sup>` -> `[9]` | M10 | {'M10': 0.675} | supported |
| c14_2 | 池化层在卷积神经网络中承担特征降维的作用。 | `[12]` -> `[10]` | M12 | {'M12': 0.682} | supported |
| c16_0 | ![图1 残差单元结构示意（引自文献）](fig1.png) | `[1]` -> `[3]` | L1-4 | {'L1-4': 0.19} | partial |
| c20_0 | AlphaFold 能够以接近实验精度预测蛋白质三维结构。 | `[11]` -> `[11]` | L2-2 | {'L2-2': 0.667} | supported |
| c20_1 | 另有研究报道残差注意力网络在多个尺度上存在普适的缩放规律。 | `[14]` -> `[12]` | M14 | {'M14': 0.57} | supported |
