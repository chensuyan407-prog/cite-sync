# cite-sync brief - case None - status partial

Done by the scripts: {"records_in": 6, "records_after_dedup": 5, "merged_clusters": 1, "occurrences_out": 4, "references_out": 4, "orphans": 1, "uncited_removed": 0, "auto_moves": 0, "verified": 0}
Consistency check: n/a
Status reasons: 1 blocking item(s) need human confirmation; 2 citation occurrence(s) whose claim-source match could not be established automatically (verdict needs_check/unverifiable): judge them in edits.occurrences; 2 citation verdict(s) are heuristic (term overlap with title/abstract), not read by a person; sources not checked online (offline run)

Write decisions to /app/work/edits.json (shape: /app/work/edits_template.json) and re-run the same command with --edits /app/work/edits.json.

## 1 Decide (blocking items / data conflicts)
- orphan_citation: marker="nokey2020" occurrences=["c4_0"] msg="in-text citation has no reference entry"

## 2 Judge these citations (heuristic could not confirm). All others carry a heuristic 'supported' you may keep
- `c2_0` needs_check: "Attention-only models were introduced in." -> Vaswani 2017 Attention is all you need
  - L1-1: no term overlap with the cited work (metadata 0.0)
- `c4_0` unverifiable: "A missing key should be reported." -> ? ? 【缺失文献：原稿引用 nokey2020 在参考文献表中找不到，需人工补充】
  - MISSING-nokey2020: no reference entry for this marker
  edit: "occurrences": {"<id>": {"verdict": "supported|partial|mismatch|unverifiable", "note": "why", "action": "keep|remove|replace|drop_refs", "refs": ["<record id>"]}}

Files: revised_manuscript=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\paper_revised.tex, references=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references_gbt7714.txt, bibtex=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references.bib, ris=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references.ris, csl_json=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references.csl.json, citation_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\citation_map.json, merge_log=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\merge_log.json, verification=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\verification.json, renumber_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\renumber_map.json, library_dedup=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\library_dedup.json, diff=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\manuscript.diff, review=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\review.md
