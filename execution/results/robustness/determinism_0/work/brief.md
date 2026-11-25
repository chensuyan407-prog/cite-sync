# cite-sync brief - case None - status partial

Done by the scripts: {"records_in": 23, "records_after_dedup": 15, "merged_clusters": 7, "occurrences_out": 13, "references_out": 12, "orphans": 0, "uncited_removed": 1, "auto_moves": 2, "verified": 0}
Consistency check: True
Status reasons: 1 claim sentence(s) without a citation (1 with a suggested library record): add a citation via edits.add_citations or leave them for the author; 13 citation verdict(s) are heuristic (term overlap with title/abstract), not read by a person; sources not checked online (offline run)

Write decisions to /app/work/edits.json (shape: /app/work/edits_template.json) and re-run the same command with --edits /app/work/edits.json.

## 2 Judge these citations (heuristic could not confirm). All others carry a heuristic 'supported' you may keep
- `c16_0` partial: "![图1 残差单元结构示意（引自文献）](fig1.png)" -> [3] He 2016 Deep Residual Learning for Image Recognition
  - L1-4: weak overlap (metadata 0.19)
  edit: "occurrences": {"<id>": {"verdict": "supported|partial|mismatch|unverifiable", "note": "why", "action": "keep|remove|replace|drop_refs", "refs": ["<record id>"]}}

## 3 Claims without a citation (add one only if a supplied record really supports it)
- u10s0: "已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训练算力呈幂律下降。" -> candidates [('L1-2', 'Scaling laws for neural language models', 0.76)]
  add_citations item: {"sentence": "text:已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训", "refs": ["L1-2"], "verdict": "supported", "note": "<why this source supports the sentence>"}

## 4 Placement
- moved M4 from u8s2 to u8s0 (support 0.0 -> 0.85)
- moved L1-1 from u8s2 to u8s1 (support 0.0 -> 0.9)

Files: revised_manuscript=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\manuscript_revised.md, references=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\references_gbt7714.txt, bibtex=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\references.bib, ris=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\references.ris, csl_json=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\references.csl.json, citation_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\citation_map.json, merge_log=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\merge_log.json, verification=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\verification.json, renumber_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\renumber_map.json, library_dedup=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\library_dedup.json, diff=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\manuscript.diff, review=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\determinism_0\output\review.md
