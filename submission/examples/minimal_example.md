# Minimal example (illustrative output, not a platform case)

Input: `examples/input/manuscript.md` (3 sentences, one paragraph-end cluster `[1][3]`, list out of order,
the Transformer cited as an arXiv preprint) and `examples/input/library.bib` (the NeurIPS version).

```bash
python scripts/cite.py init --case examples/input/case.json --out out --work work
python scripts/cite.py run --manuscript examples/input/manuscript.md --library examples/input/library.bib --out out --work work
# read work/claim_matrix.md, write work/edits.json with a verdict per occurrence, then
python scripts/cite.py run --manuscript examples/input/manuscript.md --library examples/input/library.bib --edits work/edits.json --out out --work work
```

Example output (`out/manuscript.diff`, first run):

```diff
-深度学习显著提升了视觉目标识别的性能[2]。长短期记忆网络缓解了梯度消失问题。注意力机制取代了循环结构[1][3]。
+深度学习显著提升了视觉目标识别的性能[1]。长短期记忆网络缓解了梯度消失问题[2]。注意力机制取代了循环结构[3]。
-[1] Hochreiter S, Schmidhuber J. Long short-term memory[J]. Neural Computation, 1997, 9(8): 1735-1780.
-[2] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.
-[3] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[J]. arXiv preprint arXiv:1706.03762, 2017.
+[1] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.
+[2] Hochreiter S, Schmidhuber J. Long short-term memory[J]. Neural Computation, 1997, 9(8): 1735-1780.
+[3] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems, 2017: 5998-6008.
```

`out/result.json` (excerpt, first run, offline):

```json
{"case_id": "example", "status": "partial",
 "status_reason": ["3 citation occurrence(s) without a claim-source verdict (fill edits.occurrences.*.verdict)",
                   "sources not checked online (offline run)"],
 "summary": {"records_in": 4, "records_after_dedup": 3, "merged_clusters": 1, "occurrences": 2, "occurrences_out": 3,
             "references_out": 3, "auto_moves": 1},
 "changes": [{"kind": "merge", "kept": "L1-1", "members": ["M3", "L1-1"], "rules": ["D4"]},
             {"kind": "citation_moved", "occurrence": "c2_1", "record": "M1", "from_sentence": "u2s2", "to_sentence": "u2s1"}],
 "consistency_check": {"ok": true, "max_number": 3, "list_entries": 3}}
```

`work/edits.json` for the second run:

```json
{"occurrences": {"c2_0": {"verdict": "supported"}, "c2_1": {"verdict": "supported"}, "ins_u2s1": {"verdict": "supported"}}}
```
