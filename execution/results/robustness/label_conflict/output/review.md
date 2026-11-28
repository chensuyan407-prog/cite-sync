# cite-sync review - case None

status: **partial**  
reasons: 1 blocking item(s) need human confirmation; 3 citation occurrence(s) without a claim-source verdict (fill edits.occurrences.*.verdict); sources not checked online (offline run)

## Summary
```
{
 "records_in": 3,
 "records_after_dedup": 2,
 "merged_clusters": 1,
 "occurrences": 3,
 "occurrences_out": 3,
 "references_out": 3,
 "orphans": 1,
 "uncited_removed": 0,
 "auto_moves": 0,
 "placement_suggestions": 0,
 "verified": 0,
 "verification_status_counts": {
  "unverified_offline": 2
 },
 "review_items": 2,
 "review_by_type": {
  "orphan_citation": 1,
  "weak_lexical_support": 1
 },
 "parse_problems": 1,
 "seconds": 0.01
}
```

## Numbering / list consistency (re-parsed from the written file)
ok = True; markers use 1..3; list entries 3

## Items that need a human decision

- **orphan_citation** marker=7 occurrences=['c2_2'] msg=in-text citation has no reference entry
- **weak_lexical_support** occurrence=c2_1 record=M2 score=0.0 msg=sentence shares almost no terms with the cited work: check claim-source match

## Changes

- {"kind": "merge", "kept": "M2", "members": ["M2", "M2_3"], "rules": ["D4"], "needs_review": false}

## Source verification

| record | status | issues | corrections |
|-|-|-|-|
| M1 Hochreiter 1997 Long short-term memory | unverified_offline |  |  |
| M2 LeCun 2015 Deep learning | unverified_offline |  |  |

## Citation occurrences

| occ | sentence | marker old -> new | records | support | verdict | evidence / review note |
|-|-|-|-|-|-|-|
| c2_0 | 深度学习综述见文献。 | `[2]` -> `[1]` | M2 | {'M2': 0.8} | - | - |
| c2_1 | 长短期记忆网络见。 | `[1-2]` -> `[1,2]` | M1, M2 | {'M1': 0.85, 'M2': 0.0} | - | - |
| c2_2 | 另见。 | `[7]` -> `[3]` | MISSING-7 | {'MISSING-7': 0.0} | - | - |
