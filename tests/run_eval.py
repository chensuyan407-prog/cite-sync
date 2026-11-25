"""Labelled self-evaluation of cite-sync on the author's dev/held-out cases (NOT the platform's fixed cases).

python tests/run_eval.py [--offline]

For every case the planted defects are listed in tests/cases/<case>/truth.json. Each check is evaluated on the
tool's written outputs (revised manuscript re-parsed from disk, result.json, merge_log.json). Two baselines
are scored with the same checks:
  B0  untouched manuscript (what you have before any work)
  B1  'regex renumber' - renumber [n] markers by first appearance and reorder the list; no dedup, no moves,
      no verification. This is what a quick script or a hurried agent typically does.
"""
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "submission", "scripts")
sys.path.insert(0, SCRIPTS)
import cite_doc  # noqa: E402
from cite_parse import split_reflist  # noqa: E402
from cite_common import title_key  # noqa: E402

OFFLINE = "--offline" in sys.argv


def run(case, online=True, use_edits=True):
    c = os.path.join(ROOT, "tests", "cases", case)
    t = json.load(open(os.path.join(c, "truth.json"), encoding="utf-8"))
    inp = os.path.join(c, "input")
    out, work = os.path.join(c, "output"), os.path.join(c, "work")
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "cite.py"), "init", "--case", os.path.join(inp, "case.json"), "--out", out, "--work", work],
                   capture_output=True, text=True, encoding="utf-8")
    if t.get("auto"):
        cmd = [sys.executable, os.path.join(SCRIPTS, "cite.py"), "auto", "--case", os.path.join(inp, "case.json"), "--out", out, "--work", work]
        if not online or OFFLINE:
            cmd.append("--offline")
    else:
        cmd = [sys.executable, os.path.join(SCRIPTS, "cite.py"), "run", "--manuscript", os.path.join(inp, t["manuscript"]), "--out", out, "--work", work,
               "--style", t.get("style", "gbt7714")]
    for lib in ([] if t.get("auto") else t.get("libraries", [])):
        cmd += ["--library", os.path.join(inp, lib)]
    if online and not OFFLINE and not t.get("auto"):
        cmd.append("--online")
    if t.get("edits") and use_edits:
        cmd += ["--edits", os.path.join(c, t["edits"])]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    sec = round(time.time() - t0, 2)
    if r.returncode != 0:
        print(r.stderr[-2000:])
    res = json.load(open(os.path.join(out, "result.json"), encoding="utf-8"))
    return t, res, out, sec


def parse_out(path):
    doc = cite_doc.load(path)
    occs, sents = cite_doc.analyse(doc)
    entries = [txt for _, txt in split_reflist([x for _, x in cite_doc.reflist_lines(doc)])]
    sent_refs = {}
    for o in occs:
        s = next(x for x in sents if x["id"] == o["sentence"])
        sent_refs.setdefault(s["plain"] if "plain" in s else cite_doc.plain(s["text"], []), []).extend(o.get("nums") or [])
    return doc, occs, sents, entries


def entry_of(entries, n):
    return entries[n - 1] if 0 < n <= len(entries) else ""


def sentence_numbers(doc, occs, needle):
    """numbers cited inside the sentence containing needle"""
    for ui, u in enumerate(doc["units"]):
        for s in u.get("sents", []):
            txt = u["text"][s["start"]:s["end"]]
            if needle in txt:
                return [n for o in occs if o["unit"] == ui and s["start"] <= o["start"] < s["end"] for n in (o.get("nums") or [])]
    return None


def check(t, path, res=None, merge_log=None, det_res=None, cmap=None):
    doc, occs, sents, entries = parse_out(path)
    rows = []
    for chk in t["checks"]:
        k, ok = chk["kind"], False
        if k == "order":  # list order by first appearance: entry n contains title words
            ok = len(entries) == len(chk["titles"]) and all(title_key(w) in title_key(entry_of(entries, i + 1)) for i, w in enumerate(chk["titles"]))
        elif k == "cites":  # sentence cites exactly the entries whose titles are given
            nums = sentence_numbers(doc, occs, chk["sentence"])
            got = sorted(title_key(entry_of(entries, n))[:25] for n in (nums or []))
            want = sorted(title_key(next((e for e in entries if title_key(w) in title_key(e)), "#missing#" + w))[:25] for w in chk["titles"])
            ok = nums is not None and got == want
        elif k == "not_in_list":
            ok = not any(title_key(chk["title"]) in title_key(e) for e in entries)
        elif k == "list_count":
            ok = len(entries) == chk["n"]
        elif k == "entry_contains":
            e = next((e for e in entries if title_key(chk["title"]) in title_key(e)), "")
            ok = all(x in e for x in chk["text"])
        elif k == "entry_not_contains":
            e = next((e for e in entries if title_key(chk["title"]) in title_key(e)), "")
            ok = bool(e) and not any(x in e for x in chk["text"])
        elif k == "consistent":
            from cite import check_manuscript
            ok = check_manuscript(path)["ok"]
        elif k in ("verdict_is", "evidence_found"):
            o = next((x for x in (cmap or []) if chk["sentence"] in (x.get("sentence_text") or "")), None)
            if k == "verdict_is":
                ok = bool(o) and o.get("verdict") == chk["verdict"]
            else:
                ok = bool(o) and any(e.get("page") and e.get("quote") for e in (o.get("evidence") or {}).values())
        elif k in ("suggests", "no_suggestion", "not_flagged"):
            rr = det_res if (chk.get("stage") == "detect" and det_res is not None) else res
            items = [r for r in (rr or {}).get("needs_review", []) if r["type"] == "claim_without_citation" and chk["sentence"] in r.get("text", "")]
            if k == "suggests":
                ok = bool(items) and bool(items[0].get("suggest")) and title_key(chk["title"]) in title_key(items[0]["suggest"][0]["title"] or "")
            elif k == "no_suggestion":
                ok = bool(items) and not items[0].get("suggest")
            else:
                ok = not items
        elif k == "status_is":
            rr = det_res if (chk.get("stage") == "detect" and det_res is not None) else res
            ok = bool(rr) and rr.get("status") == chk["status"]
        elif k == "contract_filled":
            ok = bool(res) and not res.get("contract_unfilled") and all(res.get(f) not in (None, "", []) for f in res.get("_contract_fields", []))
        elif k == "style_is":
            ok = {o["style"] for o in occs if o["kind"] == "num"} == {chk["style"]}
        elif k == "text_contains":
            ok = chk["text"] in "\n".join(u["text"] for u in doc["units"])
        elif k == "single_style":
            ok = len({o["style"] for o in occs if o["kind"] == "num"}) == 1
        elif k == "review":  # a review item of this type mentioning the text
            if chk.get("stage") == "detect" and det_res is not None:
                res = det_res
            ok = bool(res) and any(r["type"] == chk["type"] and (not chk.get("text") or chk["text"] in json.dumps(r, ensure_ascii=False)) for r in res.get("needs_review", []))
        elif k == "not_merged":
            ok = bool(merge_log) and not any(len(set(cl["members"]) & set(chk["ids"])) == len(chk["ids"]) for cl in merge_log["clusters"])
        elif k == "merged":
            ok = bool(merge_log) and any(set(chk["ids"]) <= set(cl["members"]) for cl in merge_log["clusters"])
        rows.append({"id": chk["id"], "kind": k, "defect": chk.get("defect", ""), "ok": bool(ok), "needs_online": chk.get("online", False),
                     "post_freeze": chk.get("post_freeze", False), "stage": chk.get("stage", "final")})
    return rows


def baseline_b1(src, dst):
    """regex renumber by first appearance, reorder list, nothing else"""
    doc = cite_doc.load(src)
    occs, _ = cite_doc.analyse(doc)
    order = []
    for o in occs:
        for n in o.get("nums") or []:
            if n not in order:
                order.append(n)
    new = {old: i + 1 for i, old in enumerate(order)}
    units = {}
    for ui, u in enumerate(doc["units"]):
        ops = [(o["start"], o["end"], o["raw"].replace(o["raw"].strip("<sup>/[]^ "), ",".join(str(new[n]) for n in o["nums"])), None)
               for o in u.get("markers", []) if o["kind"] == "num"]
        if ops:
            units[ui] = cite_doc.build_unit(u, ops)
    ents = dict(split_reflist([x for _, x in cite_doc.reflist_lines(doc)]))
    lst = [ents[o] for o in order if o in ents]
    cite_doc.save(doc, units, dst, lst)


def main():
    t0 = time.time()
    cases = [c for c in sorted(os.listdir(os.path.join(ROOT, "tests", "cases"))) if os.path.exists(os.path.join(ROOT, "tests", "cases", c, "truth.json"))]
    report = {"cases": {}, "offline": OFFLINE}
    allrows = []
    for case in cases:
        tt = json.load(open(os.path.join(ROOT, "tests", "cases", case, "truth.json"), encoding="utf-8"))
        det_res = None
        if tt.get("edits"):  # pass 1 (before the agent's edits): detection checks are scored here
            _, det_res, _, _ = run(case, use_edits=False)
            json.dump(det_res, open(os.path.join(ROOT, "tests", "cases", case, "work", "result_pass1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        t, res, out, sec = run(case)
        stem = os.path.splitext(t["manuscript"])[0]
        ext = os.path.splitext(t["manuscript"])[1]
        revised = os.path.join(out, t.get("revised") or f"{stem}_revised{ext}")
        ml = json.load(open(os.path.join(out, "merge_log.json"), encoding="utf-8"))
        cm = json.load(open(os.path.join(out, "citation_map.json"), encoding="utf-8"))
        rows = check(t, revised, res, ml, det_res, cm)
        src = os.path.join(ROOT, "tests", "cases", case, "input", t["manuscript"])
        b0 = check(t, src, None, None) if ext != ".pdf" else [{"ok": False} for _ in t["checks"]]  # a PDF is not editable: B0 passes nothing
        b1p = os.path.join(ROOT, "tests", "cases", case, "work", f"baseline_b1{ext}")
        b1 = None
        if ext not in (".tex", ".pdf"):
            baseline_b1(src, b1p)
            b1 = check(t, b1p, None, None)
        for r, x0 in zip(rows, b0):
            r["b0"] = x0["ok"]
        if b1:
            for r, x1 in zip(rows, b1):
                r["b1"] = x1["ok"]
        for r in rows:
            r["case"] = case
            r["holdout"] = t.get("holdout", False)
        allrows += rows
        report["cases"][case] = {"holdout": t.get("holdout", False), "status": res["status"], "status_reason": res["status_reason"], "seconds": sec,
                                 "checks": len(rows), "passed": sum(r["ok"] for r in rows), "b0_passed": sum(r.get("b0", False) for r in rows),
                                 "b1_passed": sum(r.get("b1", False) for r in rows) if b1 else None,
                                 "failed": [r["id"] + ": " + r["defect"] for r in rows if not r["ok"]], "summary": res["summary"]}
    def rate(rows, key):
        return round(sum(1 for r in rows if r.get(key)) / len(rows), 3) if rows else None
    dev = [r for r in allrows if not r["holdout"]]
    ho = [r for r in allrows if r["holdout"] and not r["post_freeze"]]
    ho_post = [r for r in allrows if r["holdout"] and r["post_freeze"]]
    report["dev"] = {"checks": len(dev), "skill": rate(dev, "ok"), "b0_untouched": rate(dev, "b0"), "b1_regex_renumber": rate(dev, "b1")}
    report["holdout"] = {"checks": len(ho), "skill": rate(ho, "ok"), "b0_untouched": rate(ho, "b0"), "b1_regex_renumber": rate(ho, "b1")}
    report["holdout_post_freeze_checks"] = {"checks": len(ho_post), "skill_now": rate(ho_post, "ok"),
                                            "note": "added after reading held-out outputs; failed at their freeze (v0.1: Adam glued onto the Dropout marker; v0.2: status complete with open uncited claims), fixed afterwards"}
    report["wall_seconds"] = round(time.time() - t0, 1)
    res_dir = os.path.join(ROOT, "execution", "results")
    os.makedirs(res_dir, exist_ok=True)
    json.dump(report, open(os.path.join(res_dir, "metrics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(allrows, open(os.path.join(res_dir, "eval_rows.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, ensure_ascii=False, indent=1))
    for c, v in report["cases"].items():
        print(c, v["passed"], "/", v["checks"], "b0", v["b0_passed"], "b1", v["b1_passed"], v["status"], v["failed"])


if __name__ == "__main__":
    main()
