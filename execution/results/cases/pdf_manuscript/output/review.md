# cite-sync review - case dev-pdf-manuscript

status: **partial**  
reasons: 1 citation occurrence(s) whose claim-source match could not be established automatically (verdict needs_check/unverifiable): judge them in edits.occurrences; 1 claim sentence(s) without a citation: add a citation via edits.add_citations or leave them for the author; 4 citation verdict(s) are heuristic (term overlap with title/abstract), not read by a person; sources not checked online (offline run)

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
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 4
 },
 "review_items": 3,
 "review_by_type": {
  "manuscript_converted": 1,
  "claim_without_citation": 1,
  "weak_lexical_support": 1
 },
 "parse_problems": 0,
 "seconds": 0.08
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..4; list entries 4

## Items that need a human decision

- **manuscript_converted** msg=PDF manuscript converted to editable markdown from its text layer; layout, fonts and figures are not kept - check headings and the reference list
- **claim_without_citation** sentence=u8s2 cue=has been shown text=It has been shown that dropout reduces overfitting in large networks.
- **weak_lexical_support** occurrence=c8_0 record=M2 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

## Changes

- {"kind": "manuscript_converted", "from": "C:\\Users\\12117\\Desktop\\bohrium-pdf-evidence-reader\\citesync\\tests\\cases\\pdf_manuscript\\input\\manuscript_draft.pdf", "to": "C:\\Users\\12117\\Desktop\\bohrium-pdf-evidence-reader\\citesync\\tests\\cases\\pdf_manuscript\\work\\manuscript_draft.md", "reason": "PDF manuscript converted to editable markdown from its text layer; layout, fonts and figures are not kept - check headings and the reference list"}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| M1 Vaswani 2017 Attention is all you need | unverified_offline | authors_truncated |  |
| M2 He 2016 Deep residual learning for image recogniti | unverified_offline | authors_truncated |  |
| M3 Kaplan 2020 Scaling laws for neural language model | unverified_offline | authors_truncated |  |
| M4 Ioffe 2015 Batch normalization: Accelerating deep  | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict |
|-|-|-|-|-|-|
| c4_0 | Residual learning lets networks with more than 100 layers be trained a | `[2]` -> `[1]` | M2 | {'M2': 0.38} | supported |
| c4_1 | Batch normalization normalizes layer inputs over each mini-batch and a | `[4]` -> `[2]` | M4 | {'M4': 0.24} | partial |
| c4_2 | The Transformer relies entirely on attention and dispenses with recurr | `[1]` -> `[3]` | M1 | {'M1': 0.9} | supported |
| c8_0 | The test loss of language models scales as a power law with model size | `[2]` -> `[1]` | M2 | {'M2': 0.0} | needs_check |
| c8_1 | Larger models are significantly more sample-efficient. | `[3]` -> `[4]` | M3 | {'M3': 0.19} | partial |
