# cite-sync review - case dev-pdf-evidence

status: **partial**  
reasons: 1 citation occurrence(s) whose claim-source match could not be established automatically (verdict needs_check/unverifiable): judge them in edits.occurrences; 1 claim sentence(s) without a citation: add a citation via edits.add_citations or leave them for the author; 4 citation verdict(s) are heuristic (term overlap with title/abstract or the cited PDF), not read by a person

## Summary
```
{
 "records_in": 4,
 "records_after_dedup": 4,
 "merged_clusters": 0,
 "occurrences": 5,
 "occurrences_out": 5,
 "references_out": 4,
 "orphans": 0,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 4,
 "verification_status_counts": {
  "verified_by_pdf": 2,
  "verified_with_corrections": 1,
  "verified": 1
 },
 "review_items": 5,
 "review_by_type": {
  "source_unconfirmed": 2,
  "claim_without_citation": 1,
  "weak_lexical_support": 1,
  "possible_miscitation": 1
 },
 "parse_problems": 0,
 "seconds": 0.7
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..4; list entries 4

## Items that need a human decision

- **source_unconfirmed** record=M1 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **source_unconfirmed** record=M4 msg=no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand
- **claim_without_citation** sentence=u8s2 cue=has been shown text=It has been shown that dropout reduces overfitting in large networks.
- **weak_lexical_support** occurrence=c8_0 record=M2 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match
- **possible_miscitation** occurrence=c8_0 records=['M2'] better={'record': 'M3', 'title': 'Scaling laws for neural language models', 'page': 3, 'quote': 'Dataset Size tokens Parameters non-embedding Compute PF-days, non-embedding Test Loss Figure 1 Language modeling performance improves smoothly as we increase the model size, datasetset size, and amoun', 'score': 0.692, 'cited_score': 0.231} msg=the supplied PDF of M3 matches this sentence much better (0.692 vs 0.231) than the cited work

## Changes

- {"kind": "metadata_correction", "record": "M2", "field": "doi", "old": null, "new": "10.1109/cvpr.2016.90", "source": "crossref title search"}
- {"kind": "metadata_correction", "record": "M2", "field": "authors", "old": "3 author(s)", "new": "4 authors", "source": "crossref (registry lists 4 authors; record had 3)"}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| M1 Vaswani 2017 Attention is all you need | verified_by_pdf | authors_truncated |  |
| M2 He 2016 Deep residual learning for image recogniti | verified_with_corrections |  | doi, authors |
| M3 Kaplan 2020 Scaling laws for neural language model | verified | authors_truncated |  |
| M4 Ioffe 2015 Batch normalization: Accelerating deep  | verified_by_pdf |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c4_0 | Residual learning lets networks with more than 100 layers be trained a | `[2]` -> `[1]` | M2 | {'M2': 0.38} | supported |
| c4_1 | Batch normalization normalizes layer inputs over each mini-batch and a | `[4]` -> `[2]` | M4 | {'M4': 0.24} | supported |
| c4_2 | The Transformer relies entirely on attention and dispenses with recurr | `[1]` -> `[3]` | M1 | {'M1': 0.9} | supported |
| c8_0 | The test loss of language models scales as a power law with model size | `[2]` -> `[1]` | M2 | {'M2': 0.0} | needs_check |
| c8_1 | Larger models are significantly more sample-efficient. | `[3]` -> `[4]` | M3 | {'M3': 0.19} | supported |
