# cite-sync brief - case None - status partial

Done by the scripts: {"records_in": 3, "records_after_dedup": 2, "merged_clusters": 1, "occurrences_out": 3, "references_out": 3, "orphans": 1, "uncited_removed": 0, "auto_moves": 0, "verified": 0}
Consistency check: True
Status reasons: 1 blocking item(s) need human confirmation; 2 citation occurrence(s) whose claim-source match could not be established automatically (verdict needs_check/unverifiable): judge them in edits.occurrences; 1 citation verdict(s) are heuristic (term overlap with title/abstract), not read by a person; sources not checked online (offline run)

Write decisions to /app/work/edits.json (shape: /app/work/edits_template.json) and re-run the same command with --edits /app/work/edits.json.

## 1 Decide (blocking items / data conflicts)
- orphan_citation: marker="7" occurrences=["c2_2"] msg="in-text citation has no reference entry"

## 2 Judge these citations (heuristic could not confirm). All others carry a heuristic 'supported' you may keep
- `c2_1` needs_check: "长短期记忆网络见。" -> [2] Hochreiter 1997 Long short-term memory; [1] LeCun 2015 Deep learning
  - M1: sentence shares title/abstract terms ['long', 'memory', 'short-term'] (support 0.85)
  - M2: no term overlap with the cited work (metadata 0.0)
- `c2_2` unverifiable: "另见。" -> [3] ? ? 【缺失文献：原稿引用 7 在参考文献表中找不到，需人工补充】
  - MISSING-7: no reference entry for this marker
  edit: "occurrences": {"<id>": {"verdict": "supported|partial|mismatch|unverifiable", "note": "why", "action": "keep|remove|replace|drop_refs", "refs": ["<record id>"]}}

Files: revised_manuscript=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\m_revised.md, references=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\references_gbt7714.txt, bibtex=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\references.bib, ris=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\references.ris, csl_json=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\references.csl.json, citation_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\citation_map.json, merge_log=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\merge_log.json, verification=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\verification.json, renumber_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\renumber_map.json, library_dedup=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\library_dedup.json, diff=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\manuscript.diff, review=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\label_conflict\output\review.md
