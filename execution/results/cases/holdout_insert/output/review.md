# cite-sync review - case holdout-insert

status: **partial**  
reasons: 1 blocking item(s) need human confirmation; 1 claim sentence(s) without a citation: add a citation via edits.add_citations or leave them for the author

## Summary
```
{
 "records_in": 5,
 "records_after_dedup": 5,
 "merged_clusters": 0,
 "occurrences": 0,
 "occurrences_out": 5,
 "references_out": 5,
 "orphans": 0,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 3,
 "verification_status_counts": {
  "mismatch": 1,
  "unverified_no_registry_match": 1,
  "verified": 2,
  "verified_with_corrections": 1
 },
 "review_items": 3,
 "review_by_type": {
  "source_mismatch": 1,
  "source_unconfirmed": 1,
  "claim_without_citation": 1
 },
 "parse_problems": 0,
 "seconds": 0.02
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..5; list entries 5

## Items that need a human decision

- **source_mismatch** record=L1-1 msg=DOI resolves to a different work (title differs)
- **source_unconfirmed** record=L2-1 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **claim_without_citation** sentence=u8s2 cue=有研究 text=有研究指出，量子计算将在十年内全面取代经典计算。

## Changes

- {"kind": "metadata_correction", "record": "L3-1", "field": "authors", "old": "3 author(s)", "new": "34 authors", "source": "crossref (registry lists 34 authors; record had 3)"}
- {"kind": "citation_added", "sentence": "text:研究表明，深度学习通过多层表示学习显著提升了语音识别和图像识", "records": ["L2-2"], "reason": "LeCun et al. 2015 review: deep representation learning improved speech and visual recognition", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:长短期记忆网络被广泛用于序列建模，其门控结构缓解了梯度消失问", "records": ["L3-2"], "reason": "Hochreiter & Schmidhuber 1997 introduce LSTM gates against vanishing gradients", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:卷积神经网络在 ImageNet 图像分类任务上取得了突破。", "records": ["L2-1"], "reason": "Krizhevsky et al. 2012: CNN breakthrough on ImageNet classification", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:AlphaFold 取得了接近实验精度的蛋白质结构预测结果。", "records": ["L3-1"], "reason": "Jumper et al. 2021 AlphaFold: near-experimental accuracy", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:已有研究对卷积神经网络中的池化方法进行了系统综述。", "records": ["L1-1"], "reason": "袁铭阳等 2020: survey of CNN pooling methods", "source": "edit"}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L1-1 袁铭阳 2020 卷积神经网络池化方法综述 | mismatch |  |  |
| L2-1 Krizhevsky 2012 ImageNet classification with deep  | unverified_no_registry_match |  |  |
| L2-2 LeCun 2015 Deep learning | verified |  |  |
| L3-1 Jumper 2021 Highly accurate protein structure pred | verified_with_corrections |  | authors |
| L3-2 Hochreiter 1997 Long Short-Term Memory | verified |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| ins_u4s0 | 研究表明，深度学习通过多层表示学习显著提升了语音识别和图像识别的性能。 | `` -> `[1]` | L2-2 | {'L2-2': 0.8} | supported |
| ins_u4s1 | 长短期记忆网络被广泛用于序列建模，其门控结构缓解了梯度消失问题。 | `` -> `[2]` | L3-2 | {'L3-2': 0.85} | supported |
| ins_u4s2 | 卷积神经网络在 ImageNet 图像分类任务上取得了突破。 | `` -> `[3]` | L2-1 | {'L2-1': 0.833} | supported |
| ins_u8s0 | AlphaFold 取得了接近实验精度的蛋白质结构预测结果。 | `` -> `[4]` | L3-1 | {'L3-1': 0.833} | supported |
| ins_u8s1 | 已有研究对卷积神经网络中的池化方法进行了系统综述。 | `` -> `[5]` | L1-1 | {'L1-1': 0.873} | supported |
