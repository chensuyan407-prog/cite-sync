# cite-sync review - case dev-zh-docx

status: **partial**  
reasons: 1 citation(s) removed by edit; the sentence(s) need a real source or rewording (human); 1 claim sentence(s) without a citation (1 with a suggested library record): add a citation via edits.add_citations or leave them for the author; sources not checked online (offline run)

## Summary
```
{
 "records_in": 23,
 "records_after_dedup": 15,
 "merged_clusters": 7,
 "occurrences": 11,
 "occurrences_out": 14,
 "references_out": 12,
 "orphans": 0,
 "uncited_removed": 2,
 "auto_moves": 2,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 12
 },
 "review_items": 4,
 "review_by_type": {
  "uncited_entry_removed": 2,
  "claim_without_citation": 1,
  "caption_citation": 1
 },
 "parse_problems": 0,
 "seconds": 0.13
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..12; list entries 12

## Items that need a human decision

- **uncited_entry_removed** record=M13 msg=reference-list entry never cited in the text; removed from the list: Srivastava 2014 Dropout: a simple way to prevent neural networks from overfi
- **uncited_entry_removed** record=M14 msg=reference-list entry never cited in the text; removed from the list: Smith 2019 Universal scaling of residual attention networks
- **claim_without_citation** sentence=u10s1 cue=有研究 text=另有研究报道残差注意力网络在多个尺度上存在普适的缩放规律。 suggest=[{'record': 'M14', 'score': 0.57, 'title': 'Universal scaling of residual attention networks', 'year': '2019', 'already_cited': False}] edit={'sentence': 'text:另有研究报道残差注意力网络在多个尺度上存在普适的缩放规律。', 'refs': ['M14'], 'verdict': 'supported', 'note': '<why this source supports the sentence>'}
- **caption_citation** occurrence=c8_0 msg=citation sits in a figure/table caption; check that the supported claim is in the caption, not in the body text

## Changes

- {"kind": "merge", "kept": "L1-4", "members": ["M1", "L1-4"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L1-5", "members": ["M3", "L1-5"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M6", "members": ["M6", "M8"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L1-1", "members": ["M7", "L1-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "M9", "members": ["M9", "L2-1"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L2-2", "members": ["M11", "L2-2"], "rules": ["D4"], "needs_review": false}
- {"kind": "merge", "kept": "L3-1", "members": ["M12", "L2-3", "L3-1"], "rules": ["D1", "D4"], "needs_review": false}
- {"kind": "duplicate_refs_collapsed", "occurrence": "c7_0", "old": "[6,8]", "reason": "two cited entries are the same work (see merge_log)"}
- {"kind": "citation_moved", "occurrence": "c4_0", "record": "M4", "from_sentence": "u4s2", "to_sentence": "u4s0", "reason": "lexical support 0.0 at paragraph end vs 0.85 at target sentence", "needs_review": true}
- {"kind": "citation_moved", "occurrence": "c4_0", "record": "L1-1", "from_sentence": "u4s2", "to_sentence": "u4s1", "reason": "lexical support 0.0 at paragraph end vs 0.9 at target sentence", "needs_review": true}
- {"kind": "citation_removed", "occurrence": "c10_1", "old": "[14]", "reason": "DOI 10.1038/s41586-019-9999-9 does not resolve and no matching work found in Crossref: citation removed, sentence needs a real source or deletion (human)"}
- {"kind": "citation_added", "sentence": "text:语言模型的测试损失随模型参数量", "records": ["L1-2"], "reason": "power-law scaling of loss with parameters, data and compute = Kaplan et al. 2020 (library.bib kaplan2020scaling)", "source": "edit"}
- {"kind": "markers_joined", "occurrence": "c4_0", "old": "[4][7][9]", "new": "[7]"}
- {"kind": "entry_removed_uncited", "record": "M13", "members": ["M13"]}
- {"kind": "entry_removed_uncited", "record": "M14", "members": ["M14"]}

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
| L3-1 袁铭阳 2020 卷积神经网络池化方法综述 | unverified_offline |  |  |
| M14 Smith 2019 Universal scaling of residual attention | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c2_0 | 深度学习通过多层表示学习显著提升了语音识别、视觉目标识别等任务的性能。 | `[3]` -> `[1]` | L1-5 | {'L1-5': 0.8} | supported |
| c2_1 | 卷积神经网络在 ImageNet 图像分类竞赛中取得突破，大幅降低了 top-5 错误率。 | `[5]` -> `[2]` | M5 | {'M5': 0.833} | supported |
| c2_2 | 随后，残差学习框架使得训练上百层的网络成为可能；同一团队又分析了恒等映射在残差单元中的作用。 | `[1]` -> `[3]` | L1-4 | {'L1-4': 0.57} | supported |
| c2_3 | 随后，残差学习框架使得训练上百层的网络成为可能；同一团队又分析了恒等映射在残差单元中的作用。 | `[2]` -> `[4]` | M2 | {'M2': 0.76} | supported |
| ins_u4s0 | 长短期记忆网络通过门控机制缓解了循环网络的梯度消失问题。 | `` -> `[5]` | M4 | {'M4': 0.85} | supported |
| ins_u4s1 | Transformer 完全基于注意力机制，在机器翻译任务上取得了当时最好的结果。 | `` -> `[6]` | L1-1 | {'L1-1': 0.9} | supported |
| c4_0 | BERT 通过双向预训练显著提升了多项语言理解任务的表现。 | `[4][7][9]` -> `[7]` | M9 | {'M9': 0.75} | supported |
| ins_u5s0 | 已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训练算力呈幂律下降。 | `` -> `[8]` | L1-2 | {'L1-2': 0.76} | supported |
| c7_0 | 批归一化通过减少内部协变量偏移加速了深层网络训练。 | `[6,8]` -> `[9]` | M6 | {'M6': 0.79} | supported |
| c7_1 | Adam 优化器被广泛用于训练上述模型。 | `[10]` -> `[10]` | M10 | {'M10': 0.675} | partial |
| c7_2 | 池化层在卷积神经网络中承担特征降维的作用。 | `[12]` -> `[11]` | L3-1 | {'L3-1': 0.712} | supported |
| c8_0 | 图1 残差单元结构示意（引自文献） | `[1]` -> `[3]` | L1-4 | {'L1-4': 0.19} | supported |
| c10_0 | AlphaFold 能够以接近实验精度预测蛋白质三维结构。 | `[11]` -> `[12]` | L2-2 | {'L2-2': 0.667} | supported |
| c10_1 | 另有研究报道残差注意力网络在多个尺度上存在普适的缩放规律。 | `[14]` -> `` |  | {} | unverifiable |
