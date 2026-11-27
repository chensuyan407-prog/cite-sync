# cite-sync review - case holdout-insert

status: **success**  
blocking: none  
advisory (does not lower the status): 1 claim sentence(s) without a citation and no fitting record in the inputs: left for the author (not invented)

## The six actions at a glance

| action | result |
|-|-|
| 插入/定位 placement | {"inserted": 5, "moved_from_paragraph_end": 0, "placement_suggestions": 0, "claims_without_citation": 1, "claims_with_library_candidate": 0} |
| 编号同步 renumbering | {"markers": 5, "references_out": 5, "renumbered_labels": 0, "consistency_ok": true, "order_rule": "first appearance"} |
| 去重 dedup | {"records_in": 5, "records_after": 5, "merged_clusters": 0, "rules_used": {}, "kept_apart": {}} |
| 格式 format | {"style": "gbt7714", "entries": 5, "exports": ["bibtex", "ris", "csl_json"], "records_missing_target_fields": 0} |
| 来源核验 verification | {"unverified_offline": 5} |
| 论断-文献对应 claim match | {"verdicts": {"supported": 5}, "by_agent": 5, "with_pdf_evidence": 0} |

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
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 5
 },
 "review_items": 1,
 "review_by_type": {
  "claim_without_citation": 1
 },
 "parse_problems": 0,
 "seconds": 0.02
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..5; list entries 5

## Items that need a human decision

- [advisory] **claim_without_citation** sentence=u8s2 cue=有研究 text=有研究指出，量子计算将在十年内全面取代经典计算。

## Changes

- {"kind": "citation_added", "sentence": "text:研究表明，深度学习通过多层表示学习显著提升了语音识别和图像识", "records": ["L2-2"], "reason": "LeCun et al. 2015 review: deep representation learning improved speech and visual recognition", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:长短期记忆网络被广泛用于序列建模，其门控结构缓解了梯度消失问", "records": ["L3-2"], "reason": "Hochreiter & Schmidhuber 1997 introduce LSTM gates against vanishing gradients", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:卷积神经网络在 ImageNet 图像分类任务上取得了突破。", "records": ["L2-1"], "reason": "Krizhevsky et al. 2012: CNN breakthrough on ImageNet classification", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:AlphaFold 取得了接近实验精度的蛋白质结构预测结果。", "records": ["L3-1"], "reason": "Jumper et al. 2021 AlphaFold: near-experimental accuracy", "source": "edit"}
- {"kind": "citation_added", "sentence": "text:已有研究对卷积神经网络中的池化方法进行了系统综述。", "records": ["L1-1"], "reason": "袁铭阳等 2020: survey of CNN pooling methods", "source": "edit"}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| L1-1 袁铭阳 2020 卷积神经网络池化方法综述 | unverified_offline |  |  |
| L2-1 Krizhevsky 2012 ImageNet classification with deep  | unverified_offline |  |  |
| L2-2 LeCun 2015 Deep learning | unverified_offline |  |  |
| L3-1 Jumper 2021 Highly accurate protein structure pred | unverified_offline |  |  |
| L3-2 Hochreiter 1997 Long Short-Term Memory | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| ins_u4s0 | 研究表明，深度学习通过多层表示学习显著提升了语音识别和图像识别的性能。 | `` -> `[1]` | L2-2 | {'L2-2': 0.8} | supported |
| ins_u4s1 | 长短期记忆网络被广泛用于序列建模，其门控结构缓解了梯度消失问题。 | `` -> `[2]` | L3-2 | {'L3-2': 0.85} | supported |
| ins_u4s2 | 卷积神经网络在 ImageNet 图像分类任务上取得了突破。 | `` -> `[3]` | L2-1 | {'L2-1': 0.833} | supported |
| ins_u8s0 | AlphaFold 取得了接近实验精度的蛋白质结构预测结果。 | `` -> `[4]` | L3-1 | {'L3-1': 0.833} | supported |
| ins_u8s1 | 已有研究对卷积神经网络中的池化方法进行了系统综述。 | `` -> `[5]` | L1-1 | {'L1-1': 0.873} | supported |
