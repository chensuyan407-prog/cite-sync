# cite-sync brief - case None - status success

Selected manuscript: none
Done by the scripts: {"records_in": 22, "records_after_dedup": 16, "merged_clusters": 6, "occurrences_out": 13, "references_out": 12, "orphans": 0, "uncited_removed": 1, "auto_moves": 2, "verified": 0}
Consistency check: True
Status reasons: 1 claim sentence(s) have candidate library record(s) suggested in review.md/brief.md; 13 citation verdict(s) are heuristic (term overlap with title/abstract), not read by a person; sources not checked online (offline run)

## 0 Fastest path (copy, fill, re-run - one round is enough)
1. `cp /app/work/edits_draft.json /app/work/edits.json` (the draft below, already holding every item to decide).
2. Replace each `<...>` placeholder: occurrences -> `supported` / `partial` / `mismatch` / `unverifiable` + a one-line `note`; add_citations -> `supported` to insert the citation or `reject` to leave the sentence for the author. Delete nothing else; unknown or unfilled entries are skipped, not fatal.
3. Re-run the same `auto` command with `--edits /app/work/edits.json`. Keys may also be the old marker (`"3"`) or `"text:<sentence fragment>"`; refs may be `"M3"`, `"L2-1"`, `"3"` or a BibTeX key.
```json
{
 "_help": "fill the <...> placeholders, keep or delete entries; keys starting with _ are ignored",
 "occurrences": {},
 "add_citations": [
  {
   "sentence": "text:已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训",
   "refs": [
    "L1-2"
   ],
   "verdict": "<supported|reject>",
   "note": "<why this source supports the sentence>",
   "_candidates": [
    "L1-2: Scaling laws for neural language models (0.76)"
   ]
  }
 ]
}
```

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

Files: revised_manuscript=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\manuscript_revised.md, references=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\references_gbt7714.txt, bibtex=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\references.bib, ris=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\references.ris, csl_json=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\references.csl.json, citation_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\citation_map.json, merge_log=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\merge_log.json, verification=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\verification.json, renumber_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\renumber_map.json, library_dedup=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\library_dedup.json, diff=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\manuscript.diff, review=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\corrupt_library\output\review.md
