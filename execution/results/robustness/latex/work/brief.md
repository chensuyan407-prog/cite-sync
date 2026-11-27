# cite-sync brief - case None - status success

Selected manuscript: none
Done by the scripts: {"records_in": 6, "records_after_dedup": 5, "merged_clusters": 1, "occurrences_out": 4, "references_out": 4, "orphans": 1, "uncited_removed": 0, "auto_moves": 0, "verified": 0}
Consistency check: n/a
Status reasons: 1 detected citation/source issue(s) flagged in needs_review: orphan_citation; 1 citation(s) point to an unverified or missing source (flagged in needs_review): c4_0; 1 citation(s) with no term overlap between sentence and cited work (heuristic needs_check, not judged by the agent): c2_0; 2 citation verdict(s) are heuristic (term overlap with title/abstract), not read by a person; sources not checked online (offline run)

## 0 Fastest path (copy, fill, re-run - one round is enough)
1. `cp /app/work/edits_draft.json /app/work/edits.json` (the draft below, already holding every item to decide).
2. Replace each `<...>` placeholder: occurrences -> `supported` / `partial` / `mismatch` / `unverifiable` + a one-line `note`; add_citations -> `supported` to insert the citation or `reject` to leave the sentence for the author. Delete nothing else; unknown or unfilled entries are skipped, not fatal.
3. Re-run the same `auto` command with `--edits /app/work/edits.json`. Keys may also be the old marker (`"3"`) or `"text:<sentence fragment>"`; refs may be `"M3"`, `"L2-1"`, `"3"` or a BibTeX key.
```json
{
 "_help": "fill the <...> placeholders, keep or delete entries; keys starting with _ are ignored",
 "occurrences": {
  "c2_0": {
   "verdict": "<supported|partial|mismatch|unverifiable>",
   "note": "<why, from the source>",
   "_sentence": "Attention-only models were introduced in.",
   "_refs": [
    "L1-1"
   ]
  },
  "c4_0": {
   "verdict": "<supported|partial|mismatch|unverifiable>",
   "note": "<why, from the source>",
   "_sentence": "A missing key should be reported.",
   "_refs": [
    "MISSING-nokey2020"
   ]
  }
 },
 "add_citations": []
}
```

## 1 Decide (blocking items / data conflicts)
- orphan_citation: marker="nokey2020" occurrences=["c4_0"] msg="in-text citation has no reference entry" severity="advisory"

## 2 Judge these citations (heuristic could not confirm). All others carry a heuristic 'supported' you may keep
- `c2_0` needs_check: "Attention-only models were introduced in." -> Vaswani 2017 Attention is all you need
  - L1-1: no term overlap with the cited work (metadata 0.0)
- `c4_0` unverifiable: "A missing key should be reported." -> ? ? 【缺失文献：原稿引用 nokey2020 在参考文献表中找不到，需人工补充】
  - MISSING-nokey2020: no reference entry for this marker
  edit: "occurrences": {"<id>": {"verdict": "supported|partial|mismatch|unverifiable", "note": "why", "action": "keep|remove|replace|drop_refs", "refs": ["<record id>"]}}

Files: revised_manuscript=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\paper_revised.tex, references=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references_gbt7714.txt, bibtex=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references.bib, ris=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references.ris, csl_json=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\references.csl.json, citation_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\citation_map.json, merge_log=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\merge_log.json, verification=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\verification.json, renumber_map=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\renumber_map.json, library_dedup=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\library_dedup.json, diff=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\manuscript.diff, review=C:\Users\12117\Desktop\bohrium-pdf-evidence-reader\citesync\execution\results\robustness\latex\output\review.md
