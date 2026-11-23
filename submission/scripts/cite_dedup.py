"""Explainable de-duplication.

Pairwise rules, checked in order; the first rule that fires decides the pair:

  G1  same DOI but titles disagree (sim < 0.6, no alt-title match)  -> NOT merged, conflict flagged (wrong DOI?)
  D1  same DOI                                                       -> merge
  D2  same arXiv id (version ignored)                                -> merge
  D3  title of one == title/alt-title of the other (bilingual pair)  -> merge if year/author do not contradict
  G2  different non-arXiv DOIs, same title                           -> NOT merged: two published versions
                                                                         (e.g. conference vs journal), flagged
  D4  same normalised title, first-author surname equal or unknown,
      |year diff| <= 2 (preprint <-> published allowed)              -> merge
  D5  title similarity >= 0.93, author overlap >= 0.5, |dy| <= 2      -> merge, needs_review
  G4  same title, years more than 2 apart                            -> NOT merged (reprint / new version), logged
  G3  same author set and year but titles differ                     -> NOT merged (different works), logged
                                                                         when similarity >= 0.5 (near-miss)
  H1/H2 explicit force_merge / forbid_merge edits                    -> applied as given, logged

Clusters are the connected components of merged pairs. The canonical record of a cluster prefers a published
version over a preprint, then the record with more filled fields; missing fields are filled from the other
members and each filled field records where it came from.
"""
from cite_common import (ARXIV_DOI, has_cjk, author_overlap, is_preprint, sim, surname, title_key, year_of)

FIELDS = ["title", "title_alt", "authors", "year", "container", "volume", "issue", "pages", "publisher", "place",
          "edition", "doi", "arxiv", "isbn", "url", "abstract", "keywords", "accessed"]


def _alt_match(a, b):
    ta, tb = title_key(a.get("title")), title_key(b.get("title"))
    aa, ab = title_key(a.get("title_alt")), title_key(b.get("title_alt"))
    return bool((aa and aa in (tb, ab)) or (ab and ab in (ta, aa)))


def decide(a, b):
    """-> (merge: bool|None, rule, reason, needs_review). None = rule did not apply / unrelated."""
    ts = sim(a.get("title"), b.get("title"))
    alt = _alt_match(a, b)
    da, db = (a.get("doi") or "").lower(), (b.get("doi") or "").lower()
    ya, yb = year_of(a), year_of(b)
    dy = abs(ya - yb) if ya and yb else None
    ov = author_overlap(a.get("authors"), b.get("authors"))
    fa = surname((a.get("authors") or [None])[0]), surname((b.get("authors") or [None])[0])
    if da and da == db:
        if has_cjk(a.get("title")) != has_cjk(b.get("title")):
            return True, "D1", f"same DOI {da}; titles in two languages (bilingual record of one article)", False
        if ts < 0.6 and not alt:
            return False, "G1", f"same DOI {da} but titles differ (similarity {ts:.2f}); one DOI is probably wrong", True
        return True, "D1", f"same DOI {da}", False
    if a.get("arxiv") and a.get("arxiv") == b.get("arxiv"):
        return True, "D2", f"same arXiv id {a['arxiv']}", ts < 0.8
    if alt:
        if dy is not None and dy > 1:
            return False, "G1", f"bilingual titles match but years differ ({ya} vs {yb})", True
        return True, "D3", "title of one record equals the translated/alternate title of the other", False
    real_doi = lambda d: d and not ARXIV_DOI.match(d)
    if ts == 1.0 and real_doi(da) and real_doi(db) and da != db:
        return False, "G2", f"same title but two different publisher DOIs ({da}, {db}): separate published versions; choose one by hand", True
    first_ok = (not fa[0] or not fa[1] or fa[0] == fa[1] or (ov or 0) >= 0.5)
    if ts == 1.0 and first_ok and (dy is None or dy <= 2):
        pre = is_preprint(a) != is_preprint(b)
        return True, "D4", "same normalised title, same first author" + (", preprint and published version" if pre else "") + (f", years {ya}/{yb}" if dy else ""), False
    if ts >= 0.93 and (ov is None or ov >= 0.5) and (dy is None or dy <= 2):
        return True, "D5", f"near-identical titles (similarity {ts:.2f}), author overlap {ov if ov is None else round(ov, 2)}", True
    if ts == 1.0 and dy is not None and dy > 2:
        return False, "G4", f"same title but years {ya}/{yb} far apart: treated as different versions (e.g. reprint); choose one by hand", False
    if ov is not None and ov >= 0.99 and dy == 0 and ts >= 0.5:
        return False, "G3", f"same authors and year, but different titles (similarity {ts:.2f}): different works", False
    return None, "", "", False


def _filled(r):
    return sum(1 for f in FIELDS if r.get(f))


def dedup(records, force=(), forbid=()):
    """-> (canonical records, merge_log, conflicts). Input records need unique 'id'.
    force / forbid: pairs of record ids decided by a human or the agent (rule H1 / H2, logged)."""
    n = len(records)
    parent = list(range(n))
    pos = {r["id"]: i for i, r in enumerate(records)}
    forced = {frozenset(p) for p in force}
    forbidden = {frozenset(p) for p in forbid}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    log, conflicts, pair_review = [], [], set()
    for i in range(n):
        for j in range(i + 1, n):
            key = frozenset((records[i]["id"], records[j]["id"]))
            if key in forbidden:
                m, rule, why, review = False, "H2", "kept separate by explicit edit (forbid_merge)", False
            elif key in forced:
                m, rule, why, review = True, "H1", "merged by explicit edit (force_merge)", False
            else:
                m, rule, why, review = decide(records[i], records[j])
            if m is None:
                continue
            ent = {"a": records[i]["id"], "b": records[j]["id"], "rule": rule, "merged": m, "reason": why, "needs_review": review}
            log.append(ent)
            if m:
                ri, rj = find(i), find(j)
                bad = any(frozenset((records[a]["id"], records[b]["id"])) in forbidden
                          for a in range(n) if find(a) == ri for b in range(n) if find(b) == rj)
                if bad:
                    ent.update(merged=False, reason=ent["reason"] + "; blocked: would join records kept separate by edit")
                    continue
                parent[ri] = rj
                if review:
                    pair_review.add((i, j))
            elif rule in ("G1", "G2"):
                conflicts.append(ent)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    out = []
    for members in sorted(groups.values(), key=lambda g: min(g)):
        recs = [records[i] for i in members]
        canon = sorted(recs, key=lambda r: (is_preprint(r), -_filled(r), records.index(r)))[0]
        c = {k: v for k, v in canon.items()}
        c["merged_from"] = [r["id"] for r in recs]
        prov = {}
        for r in recs:
            if r is canon:
                continue
            for f in FIELDS:
                if not c.get(f) and r.get(f):
                    if f == "title_alt" and title_key(r.get("title")) != title_key(c.get("title")):
                        pass
                    c[f] = r[f]
                    prov[f] = r["id"]
            if title_key(r.get("title")) != title_key(c.get("title")) and r.get("title") and not c.get("title_alt"):
                c["title_alt"] = r["title"]
                prov["title_alt"] = r["id"]
            if is_preprint(r) and not is_preprint(canon) and r.get("arxiv"):
                c["arxiv"] = r["arxiv"]
                c["preprint_merged"] = r["id"]
        longest = max((r.get("authors") or [] for r in recs), key=len)
        if len(longest) > len(c.get("authors") or []):
            c["authors"] = longest
            prov["authors"] = next(r["id"] for r in recs if (r.get("authors") or []) is longest)
        trunc = [r for r in recs if r.get("authors_truncated")]
        if trunc and len(c.get("authors") or []) <= max(len(r.get("authors") or []) for r in trunc) + 0:
            c["authors_truncated"] = True  # a member says 'et al.' and no member lists more names
        elif trunc:
            c.pop("authors_truncated", None)
        if prov:
            c["field_provenance"] = prov
        c["merge_needs_review"] = any(i in members and j in members for i, j in pair_review)
        out.append(c)
    return out, log, conflicts
