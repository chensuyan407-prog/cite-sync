#!/usr/bin/env python3
"""Port an edits.json written for one run to another run whose occurrence ids differ
(manuscript edited, converted md <-> docx, paragraphs re-flowed).

  python port_edits.py --edits old_edits.json --old-map old/citation_map.json --new-map new/citation_map.json --out new_edits.json

An occurrence is matched by (sentence text without markers, old marker text); moved/inserted ones (ins_<sentence>)
by sentence text. Unmatched entries are listed on stdout and left out, never guessed.
"""
import argparse
import json
import re


def key(o):
    """sentence letters/digits only (drops markdown/caption syntax) + the marker's numbers/keys only"""
    s = re.sub(r"\(\S+\.(png|jpg|svg|pdf)\)", "", o.get("sentence_text") or "")
    s = "".join(ch for ch in s if ch.isalnum())
    m = re.sub(r"<[^>]+>|[\^\[\]［］\s]", "", o.get("old") or "")
    return s, m


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--edits", required=True)
    p.add_argument("--old-map", required=True)
    p.add_argument("--new-map", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    ed = json.load(open(a.edits, encoding="utf-8"))
    old = {o["id"]: o for o in json.load(open(a.old_map, encoding="utf-8"))}
    new = json.load(open(a.new_map, encoding="utf-8"))
    by_key = {}
    for o in new:
        k = (key(o)[0], "*ins*") if o["id"].startswith("ins_") else key(o)
        by_key.setdefault(k, []).append(o["id"])
    out, unmatched = {}, []
    for oid, e in (ed.get("occurrences") or {}).items():
        o = old.get(oid)
        if not o:
            unmatched.append(oid)
            continue
        k = (key(o)[0], "*ins*") if oid.startswith("ins_") else key(o)
        hits = by_key.get(k, [])
        if len(hits) == 1:
            out[hits[0]] = e
        else:
            unmatched.append(oid)
    ed["occurrences"] = out
    json.dump(ed, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"ported": len(out), "unmatched": unmatched, "note": "add_citations / move_to with 'text:' sentence addresses port unchanged; u<i>s<k> ids do not"}, indent=1))


if __name__ == "__main__":
    main()
