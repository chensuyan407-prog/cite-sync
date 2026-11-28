#!/usr/bin/env python3
"""cite-sync command line.

  cite.py init    --case /input/case.json --out /app/output --work /app/work
  cite.py run     --manuscript M [--library L ...] [--style gbt7714|apa7] [--online] [--edits E] --out O --work W
  cite.py check   --manuscript M [--style gbt7714]          (consistency check of any numbered manuscript)
  cite.py convert --library L [...] --to gbt7714|apa7|bibtex|ris|csl [--dedup] [--online] --out FILE

Exit code 0 even when problems are found (they are reported); 2 for unusable input.
"""
import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cite_common import (dump, has_cjk, load as jload, norm_doi, read_text, sha256, short, sim, surname, title_key,  # noqa: E402
                         write, year_of)
import cite_doc  # noqa: E402
import cite_format as F  # noqa: E402
from cite_dedup import dedup  # noqa: E402
from cite_parse import load_library, parse_refstring, split_reflist  # noqa: E402
import cite_verify as V  # noqa: E402

VERSION = "0.1.0"
MS_EXT = (".md", ".markdown", ".docx", ".tex", ".txt")
LIB_EXT = (".bib", ".bibtex", ".ris", ".enw", ".endnote", ".json", ".csl", ".txt", ".net")


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- init
def cmd_init(a, save=True):
    t0 = time.time()
    out, work = a.out, a.work
    os.makedirs(out, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    case, case_err = {}, None
    if not os.path.exists(a.case):
        case_err = f"{a.case} not found"
    else:
        try:
            case = jload(a.case)
            if not isinstance(case, dict):
                case, case_err = {}, "case.json must contain an object"
        except Exception as e:
            case_err = f"case.json unreadable: {e!r}"
    base = os.path.dirname(os.path.abspath(a.case))
    files = []
    excluded = {os.path.abspath(path) for path in (out, work)}
    for root, dirs, names in os.walk(base):
        dirs[:] = sorted(name for name in dirs if not name.startswith(".") and os.path.join(root, name) not in excluded)
        files.extend(os.path.join(root, name) for name in sorted(names) if not name.startswith("."))
    named = []
    preferred = {"manuscript": [], "library": []}

    def walk(value, role=None):
        if isinstance(value, str):
            for candidate in (os.path.join(base, value), os.path.join(base, "input", value)):
                if os.path.isfile(candidate):
                    path = os.path.abspath(candidate)
                    named.append(path)
                    if role:
                        preferred[role].append(path)
                    break
        elif isinstance(value, dict):
            for key, item in value.items():
                if key == "output_contract":
                    continue
                child = role
                if re.search(r"manuscript|draft|^paper$|main_paper|稿", key, re.I):
                    child = "manuscript"
                elif re.search(r"librar|bibliograph|references|文献库", key, re.I):
                    child = "library"
                walk(item, child)
        elif isinstance(value, list):
            for item in value:
                walk(item, role)

    walk(case)
    task = next((p for p in files if os.path.basename(p).lower() in ("task.md", "task.txt")), None)
    ms, libs, pdfs, other = [], [], [], []
    for p in sorted(set(files + named)):
        b = os.path.basename(p).lower()
        ext = os.path.splitext(b)[1]
        if p == task or p == os.path.abspath(a.case) or p in preferred["library"] or p in preferred["manuscript"]:
            continue
        if ext == ".pdf":
            pdfs.append(p)
            continue
        txt = ""
        if ext in (".json", ".txt"):
            with open(p, "rb") as stream:
                txt = stream.read(20000).decode("utf-8-sig", "replace")
        looks_lib = ext in (".bib", ".bibtex", ".ris", ".enw", ".endnote", ".net", ".csl") or bool(
            re.search(r"^\s*@\w+\s*\{|^TY  - |^%0 |^\{Reference Type\}", txt, re.M)) or (ext == ".json" and re.search(r'"(title|DOI|author)"', txt))
        looks_ms = ext in (".md", ".markdown", ".docx", ".tex") or (ext == ".txt" and len(re.findall(r"[\[［]\d+[\]］]", txt)) >= 3 and len(txt) > 40)
        if looks_lib:
            libs.append(p)
        elif looks_ms:
            ms.append(p)
        else:
            other.append(p)
    hint = {k: v for k, v in case.items() if isinstance(v, (str, int, float)) and k not in ("case_id",)} if isinstance(case, dict) else {}
    hint_style = next((case[k] for k in ("target_style", "citation_style", "reference_style", "style") if case.get(k)), None)
    style = guess_style(str(hint_style) if hint_style else (read_text(task) if task else ""))
    ms = list(dict.fromkeys(preferred["manuscript"])) or sorted(ms, key=lambda path: (
        not bool(re.search(r"manuscript|draft|paper|正文|稿", os.path.basename(path), re.I)),
        bool(re.search(r"readme|notes|说明", os.path.basename(path), re.I)), path))
    libs = list(dict.fromkeys(preferred["library"] + libs))
    contract = contract_fields(case)
    inv = {"case_id": case.get("case_id", case.get("id")), "case_error": case_err, "task_file": task,
           "manuscripts": ms, "libraries": libs, "pdfs": pdfs, "other_files": other, "output_contract": contract,
           "style_guess": style, "case_scalars": hint, "seconds": round(time.time() - t0, 2)}
    dump(os.path.join(work, "inventory.json"), inv)
    res = base_result(inv["case_id"], contract)
    res["status"] = "failed" if case_err or not (ms or libs) else "partial"
    res["status_reason"] = case_err or ("no manuscript or reference library found in the input" if not (ms or libs) else
                                        "init only: run `cite.py run` next")
    res["inputs"] = {"case": a.case, "task": task, "manuscripts": [fi(p) for p in ms], "libraries": [fi(p) for p in libs], "pdfs": [fi(p) for p in pdfs]}
    if save:
        if not os.path.exists(os.path.join(out, "result.json")):
            save_result(out, res, contract, True)
        print(json.dumps(inv, ensure_ascii=False, indent=1))
    return inv, res


def fi(p):
    return {"path": p, "sha256": sha256(p), "bytes": os.path.getsize(p)}


def guess_style(text):
    t = text.lower()
    if re.search(r"apa", t):
        return "apa7"
    return "gbt7714"


def contract_fields(case):
    contract = case.get("output_contract")
    if isinstance(contract, dict):
        properties = contract.get("properties")
        fields = dict(properties) if isinstance(properties, dict) else dict(contract)
        if isinstance(contract.get("required"), list):
            fields.pop("required", None)
            for name in contract["required"]:
                if isinstance(name, str):
                    fields.setdefault(name, None)
        return fields
    if isinstance(contract, list):
        fields = {}
        for item in contract:
            name = item if isinstance(item, str) else (item.get("name") or item.get("field")) if isinstance(item, dict) else None
            if isinstance(name, str) and name:
                fields[name] = item if isinstance(item, dict) else None
        return fields
    return {}


def save_result(out, report, contract, clean):
    def write_atomic(name, content):
        with tempfile.NamedTemporaryFile(dir=out, delete=False) as stream:
            temp = stream.name
        try:
            dump(temp, content)
            os.replace(temp, os.path.join(out, name))
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    result = report
    if clean and contract:
        # Keep case_id, run status, all output_contract fields (and nested output_contract), plus core deliverables
        # (artifacts, references_list, changes, needs_review, consistency_check, summary) in result.json with paths relative to out/.
        out_abs = os.path.abspath(out)
        def relative(value):
            if isinstance(value, str) and os.path.isabs(value) and value.startswith(out_abs):
                return os.path.relpath(value, out).replace("\\", "/")
            if isinstance(value, list):
                return [relative(v) for v in value]
            if isinstance(value, dict):
                return {k: relative(v) for k, v in value.items()}
            return value
        contract_obj = {key: relative(report.get(key)) for key in contract if key != "case_id"}
        result = {"case_id": report.get("case_id"), "status": report.get("status"), "status_reason": report.get("status_reason"),
                  **contract_obj, "output_contract": contract_obj}
        for extra in ("artifacts", "references_list", "changes", "needs_review", "consistency_check", "summary", "inputs", "uncertainty"):
            if extra not in result and extra in report:
                result[extra] = relative(report.get(extra))
        write_atomic("run_report.json", report)
    write_atomic("result.json", result)


def base_result(case_id, contract):
    r = {"case_id": case_id, "tool": f"cite-sync {VERSION}", "status": "partial"}
    for f in contract:
        r.setdefault(f, None)
    return r


# ---------------------------------------------------------------- run
def resolve_ay(item, recs):
    sn = title_key(re.split(r"\s+(?:et al|and|&)|等|和", item["name"])[0])
    cands = [r for r in recs if str(r.get("year")) == item["year"] and r.get("authors") and
             (surname(r["authors"][0]) == sn or title_key(r["authors"][0].get("literal", ""))[:len(sn)] == sn or
              title_key(r["authors"][0].get("family", "") + r["authors"][0].get("given", "")) == sn)]
    if item.get("suffix"):
        c2 = [r for r in cands if r.get("year_suffix") == item["suffix"]]
        cands = c2 or cands
    return cands


def pdf_manuscript(path, work):
    import pymupdf as fitz

    blocks = []
    with fitz.open(path) as pdf:
        if pdf.needs_pass:
            raise ValueError("PDF is password protected")
        for page in pdf:
            for block in page.get_text("blocks", sort=True):
                if block[6] != 0:
                    continue
                text = block[4].strip()
                if text and not text.isdecimal():
                    blocks.append(text)
    if not blocks:
        raise ValueError("PDF has no extractable text; supply OCR text or an editable manuscript")
    target = os.path.join(work, os.path.splitext(os.path.basename(path))[0] + ".md")
    write(target, "\n\n".join(blocks) + "\n")
    return target


def cmd_run(a):
    t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    inv = {}
    a.case = a.case or ("/input/case.json" if not a.manuscript and not a.library and os.path.isfile("/input/case.json") else None)
    a.clean = bool(a.case)
    inventory_path = os.path.join(a.work, "inventory.json")
    if a.case:
        inv, _ = cmd_init(a, save=False)
        a.manuscript = a.manuscript or next(iter(inv["manuscripts"]), None)
        a.library = a.library or inv["libraries"]
        a.style = a.style or inv["style_guess"]
    elif os.path.isfile(inventory_path):
        inv = jload(inventory_path)
    if inv.get("case_id") is not None:
        a.case_id = inv["case_id"]
    a.contract = inv.get("output_contract") or {}
    a.previous = {}
    result_path = os.path.join(a.out, "result.json")
    if os.path.exists(result_path):
        try:
            a.previous = jload(result_path)
        except (OSError, ValueError):
            a.previous = None
        if (not isinstance(a.previous, dict)
                or a.previous.get("case_id") is not None and a.previous.get("case_id") != a.case_id):
            log("result.json belongs to another case or is unreadable; choose a different output directory")
            raise SystemExit(2)
    review, changes, problems = [], [], []
    edits = {}
    if a.edits:
        try:
            supplied = jload(a.edits)
            if not isinstance(supplied, dict):
                raise ValueError("edits must contain an object")
            edits = supplied
        except (OSError, ValueError) as exc:
            review.append({"type": "invalid_edits", "msg": str(exc)})
    if inv.get("case_error"):
        review.append({"type": "case_input", "msg": inv["case_error"]})
    style = a.style or "gbt7714"
    doc = None
    original_manuscript = a.manuscript
    if a.clean and a.manuscript and a.manuscript.lower().endswith(".pdf"):
        try:
            a.manuscript = pdf_manuscript(a.manuscript, a.work)
            review.append({"type": "pdf_text_conversion", "msg": "Review the recovered Markdown against the PDF, including layout and figures"})
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            fail(a, f"PDF manuscript could not be extracted: {exc}", [])
    if a.manuscript:
        try:
            doc = cite_doc.load(a.manuscript)
        except Exception as e:
            fail(a, f"manuscript not usable: {e}", [])
            return
        occs, sents = cite_doc.analyse(doc)
        doc["zh"] = sum(1 for u in doc["units"] if has_cjk(u["text"])) > len(doc["units"]) / 4
    else:
        occs, sents = [], []
    # ---------------- records: manuscript list + libraries
    records = []
    if doc and doc["ref_start"] is not None and doc["kind"] != "tex":
        for k, (num, txt) in enumerate(split_reflist([t for _, t in cite_doc.reflist_lines(doc)]), 1):
            r = parse_refstring(txt, os.path.basename(a.manuscript), k)
            r["label"] = num if num is not None else k
            r["id"] = f"M{r['label']}"
            if any(x["id"] == r["id"] for x in records):
                r["id"] = f"M{r['label']}_{k}"
                problems.append({"file": os.path.basename(a.manuscript), "index": k, "problem": f"reference list label [{num}] used twice"})
            r["origin"] = "manuscript_list"
            records.append(r)
    for li, lp in enumerate(a.library or []):
        if not os.path.exists(lp):
            problems.append({"file": lp, "index": 0, "problem": "library file not found"})
            continue
        recs, probs, fmt = load_library(lp)
        problems += probs
        for r in recs:
            r["id"] = f"L{li + 1}-{r['src']['index']}"
            r["origin"] = f"library:{os.path.basename(lp)}"
            records.append(r)
    for rid, ov in (edits.get("record_overrides") or {}).items():
        for r in records:
            if r["id"] == rid:
                src = ov.pop("_source", "agent edit")
                for k, v in ov.items():
                    changes.append({"kind": "record_field_edit", "record": rid, "field": k, "old": r.get(k), "new": v, "source": src})
                    r[k] = v
    for r in records:
        r["doi"] = norm_doi(r.get("doi"))
    if not records:
        fail(a, "no reference records found (no reference list in the manuscript and no readable library)", problems)
        return
    canon, mlog, conflicts = dedup(records, edits.get("force_merge") or [], edits.get("forbid_merge") or [])
    id2c = {}
    for c in canon:
        c["cid"] = c["merged_from"][0] if len(c["merged_from"]) == 1 else c["id"]
        for m in c["merged_from"]:
            id2c[m] = c
    for c in canon:
        if len(c["merged_from"]) > 1:
            changes.append({"kind": "merge", "kept": c["id"], "members": c["merged_from"],
                            "rules": sorted({e["rule"] for e in mlog if e["merged"] and e["a"] in c["merged_from"]}),
                            "needs_review": c.get("merge_needs_review", False)})
            if c.get("merge_needs_review"):
                review.append({"type": "merge_uncertain", "records": c["merged_from"], "msg": "merge decided by fuzzy title match; confirm"})
    for e in conflicts:
        review.append({"type": "dedup_conflict", "records": [e["a"], e["b"]], "rule": e["rule"], "msg": e["reason"]})
    # ---------------- resolve occurrences
    if any(o["kind"] == "ay" for o in occs):  # author-year: 2016a / 2016b by title order (APA rule) before matching
        grp = {}
        for c in canon:
            grp.setdefault((F.author_year_label(dict(c, year_suffix="")), str(c.get("year"))), []).append(c)
        for g in grp.values():
            if len(g) > 1:
                for i, c in enumerate(sorted(g, key=lambda r: title_key(r.get("title")))):
                    c["year_suffix"] = "abcdefghij"[i]
    label2id = {r["label"]: r["id"] for r in records if r.get("origin") == "manuscript_list"}
    lib_by_label = {r["label"]: r["id"] for r in records if r.get("origin", "").startswith("library") and r.get("label") is not None}
    key2id = {}
    for r in records:
        if r.get("bibkey"):
            key2id.setdefault(r["bibkey"], r["id"])
    orphans = {}
    for o in occs:
        o["cids"] = []
        o["unresolved"] = []
        if o["kind"] == "num":
            for n in o["nums"]:
                rid = label2id.get(n) or (lib_by_label.get(n) if not label2id else None)
                if rid:
                    o["cids"].append(id2c[rid]["id"])
                else:
                    o["unresolved"].append(n)
        elif o["kind"] == "key":
            for k in o["keys"]:
                rid = key2id.get(k)
                (o["cids"].append(id2c[rid]["id"]) if rid else o["unresolved"].append(k))
        else:
            for it in o["ay"]:
                c = resolve_ay(it, canon)
                if len(c) == 1:
                    o["cids"].append(c[0]["id"])
                else:
                    o["unresolved"].append(f"{it['name']} {it['year']}{it.get('suffix', '')}" + (" (ambiguous)" if c else ""))
        if len(set(o["cids"])) < len(o["cids"]):
            changes.append({"kind": "duplicate_refs_collapsed", "occurrence": o["id"], "old": o["raw"], "reason": "two cited entries are the same work (see merge_log)"})
            o["cids"] = list(dict.fromkeys(o["cids"]))
        for u in o["unresolved"]:
            orphans.setdefault(str(u), []).append(o["id"])
    # placeholder records for markers that point nowhere (numbering stays consistent and visible)
    for u, oids in orphans.items():
        ph = {"id": f"MISSING-{u}", "type": "misc", "title": f"【缺失文献：原稿引用 {u} 在参考文献表中找不到，需人工补充】",
              "placeholder": True, "merged_from": [f"MISSING-{u}"]}
        canon.append(ph)
        id2c[ph["id"]] = ph
        review.append({"type": "orphan_citation", "marker": u, "occurrences": oids, "msg": "in-text citation has no reference entry"})
        for o in occs:
            if o["id"] in oids:
                o["cids"].append(ph["id"])
    byid = {c["id"]: c for c in canon}
    # ---------------- online / offline verification of records that matter
    cited_ids = {c for o in occs for c in o["cids"]}
    targets = [c for c in canon if not c.get("placeholder")
               and (c["id"] in cited_ids or not occs or a.clean and a.edits)]
    targets.sort(key=lambda c: c["id"] not in cited_ids)
    net = V.Net(os.path.join(a.work, "net_cache.json"), enabled=a.online, budget_s=a.net_budget,
                max_requests=a.net_max_requests, timeout=a.net_timeout)
    verification = {}
    for c in targets:
        st, det, corr = V.online_check(net, c) if a.online else ("unverified_offline", {"reason": "online checks not requested (--online)"}, {})
        applied = {}
        if corr and a.apply_corrections:
            for f, (old, new, src) in corr.items():
                if f == "doi" and st == "verified_with_corrections" and det.get("doi_not_found"):
                    pass
                c[f] = new
                applied[f] = {"old": old, "new": new, "source": src}
                c.setdefault("field_provenance", {})[f] = src
                changes.append({"kind": "metadata_correction", "record": c["id"], "field": f, "old": old, "new": new, "source": src})
        iss = V.offline_checks(c, style)
        verification[c["id"]] = {"status": st, "details": det, "corrections": applied, "issues": iss, "record": short(c)}
        if st in ("not_found", "doi_not_found", "mismatch"):
            review.append({"type": "source_" + st, "record": c["id"], "msg": det.get("problem") or ("DOI does not resolve" if st == "doi_not_found" else "no matching record found in Crossref/arXiv: possibly fabricated or mis-cited"), "details": det})
        if st == "unverified_offline" and a.clean and a.online:
            review.append({"type": "source_unconfirmed", "record": c["id"], "msg": det.get("reason") or "offline verification only"})
        if st == "unverified_no_registry_match":
            review.append({"type": "source_unconfirmed", "record": c["id"], "msg": "no Crossref/arXiv record with matching title+authors+year; common for proceedings without DOI, books, Chinese journals - check by hand", "details": det.get("search_best")})
        for i in iss:
            if i["severity"] == "error":
                review.append({"type": "metadata_" + i["code"], "record": c["id"], "msg": i["msg"]})
        if det.get("published_version"):
            review.append({"type": "preprint_has_published_version", "record": c["id"], "msg": "a published version exists; cite it instead of the preprint?", "details": det["published_version"]})
    net.save()
    # ---------------- support hints per occurrence and placement analysis
    sent_by_id = {s["id"]: s for s in sents}
    for s in sents:
        u = doc["units"][s["unit"]]
        s["plain"] = cite_doc.plain(u["text"][s["start"]:s["end"]], [dict(m, start=m["start"] - s["start"], end=m["end"] - s["start"]) for m in u["markers"] if s["start"] <= m["start"] < s["end"]])
    moves = []
    for o in occs:
        s = sent_by_id.get(o["sentence"])
        o["support"] = {}
        for cid in o["cids"]:
            c = byid[cid]
            o["support"][cid] = V.support(s["plain"] if s else "", c) if not c.get("placeholder") else (0.0, [])
        # P1: cluster at the end of a multi-sentence paragraph: does each source fit an earlier sentence better?
        if s and s["is_last_in_unit"] and s["n_in_unit"] >= 2 and o["kind"] != "ay" and not o.get("narrative"):
            unit_sents = [x for x in sents if x["unit"] == o["unit"]]
            for cid in o["cids"]:
                c = byid[cid]
                if c.get("placeholder"):
                    continue
                here = o["support"][cid][0]
                best = max(unit_sents, key=lambda x: V.support(x["plain"], c)[0])
                bs = V.support(best["plain"], c)[0]
                if best["id"] != s["id"] and bs >= 0.3 and bs >= 3 * max(here, 0.05):
                    moves.append({"occ": o["id"], "cid": cid, "from": s["id"], "to": best["id"], "score_from": here, "score_to": bs,
                                  "auto": bool(a.auto_move) and len(o["cids"]) >= 2})
    # ---------------- apply occurrence edits + automatic moves
    occ_by_id = {o["id"]: o for o in occs}
    verdicts = {}
    adds = []  # (sentence_id, [cids], reason, assessment)
    for mv in moves:
        override = (edits.get("occurrences") or {}).get(mv["occ"], {})
        if mv["auto"] and override.get("action", "keep") == "keep" and not override.get("move_to"):
            o = occ_by_id[mv["occ"]]
            if mv["cid"] in o["cids"] and len(o["cids"]) > 1:
                o["cids"].remove(mv["cid"])
                adds.append((mv["to"], [mv["cid"]], f"moved from paragraph-end cluster {o['raw']} (support {mv['score_from']} -> {mv['score_to']})", {}))
                changes.append({"kind": "citation_moved", "occurrence": o["id"], "record": mv["cid"], "from_sentence": mv["from"], "to_sentence": mv["to"],
                                "reason": f"lexical support {mv['score_from']} at paragraph end vs {mv['score_to']} at target sentence", "needs_review": True})
        else:
            review.append({"type": "citation_placement", "occurrence": mv["occ"], "record": mv["cid"], "msg": f"source fits sentence {mv['to']} better than the paragraph-end position ({mv['score_from']} vs {mv['score_to']})",
                           "suggest": {"move_to": mv["to"]}})

    def to_cids(lst):
        out = []
        for x in lst:
            x = str(x)
            if x in id2c:
                out.append(id2c[x]["id"])
            elif x.isdigit() and int(x) in label2id:
                out.append(id2c[label2id[int(x)]]["id"])
            elif x in key2id:
                out.append(id2c[key2id[x]]["id"])
            else:
                problems.append({"file": "edits", "index": 0, "problem": f"edit refers to unknown record {x}"})
        return out

    for oid, e in (edits.get("occurrences") or {}).items():
        o = occ_by_id.get(oid)
        if oid.startswith("ins_"):
            verdicts[oid] = e
            continue
        if not o:
            problems.append({"file": "edits", "index": 0, "problem": f"unknown occurrence {oid}"})
            continue
        if e.get("verdicts") or e.get("verdict"):
            verdicts[oid] = e
        act = e.get("action", "keep")
        if act == "remove":
            changes.append({"kind": "citation_removed", "occurrence": oid, "old": o["raw"], "reason": e.get("note", "")})
            o["cids"] = []
            o["removed"] = True
        elif act == "replace":
            if a.clean and not (e.get("evidence") or e.get("note")):
                review.append({"type": "replacement_not_applied", "occurrence": oid, "msg": "provide a source locator for this replacement"})
                verdicts.pop(oid, None)
                continue
            refs = e.get("refs") or []
            new = to_cids(refs)
            if not new or len(new) != len(refs):
                review.append({"type": "replacement_not_applied", "occurrence": oid, "msg": "replacement record could not be resolved"})
                verdicts.pop(oid, None)
                continue
            changes.append({"kind": "citation_replaced", "occurrence": oid, "old": o["cids"], "new": new, "reason": e.get("note", ""), "evidence": e.get("evidence") or e.get("note")})
            o["cids"] = new
            o["unresolved"] = []
        elif act == "drop_refs":
            dr = set(to_cids(e.get("refs", [])))
            changes.append({"kind": "citation_refs_dropped", "occurrence": oid, "dropped": sorted(dr), "reason": e.get("note", "")})
            o["cids"] = [c for c in o["cids"] if c not in dr]
        if e.get("move_to"):
            mv_c = to_cids(e.get("move_refs") or []) or list(o["cids"])
            o["cids"] = [c for c in o["cids"] if c not in mv_c]
            adds.append((e["move_to"], mv_c, e.get("note", "agent move"), e))
            changes.append({"kind": "citation_moved", "occurrence": oid, "records": mv_c, "from_sentence": o["sentence"], "to_sentence": e["move_to"], "reason": e.get("note", ""), "source": "edit"})
    for ad in edits.get("add_citations") or []:
        if a.clean and not (ad.get("evidence") or ad.get("note")):
            review.append({"type": "insertion_not_applied", "sentence": ad.get("sentence"), "msg": "provide a source locator for this insertion"})
            continue
        c = to_cids(ad.get("refs", []))
        if c and ad.get("sentence"):
            adds.append((ad["sentence"], c, ad.get("evidence") or ad.get("note", "agent addition"), ad))
    # ---------------- build ordered occurrence list (originals + insertions) and number by first appearance
    numeric = style != "apa7" and not (doc and doc["kind"] == "tex")
    style_counts = {}
    for o in occs:
        if o["kind"] == "num":
            style_counts[o["style"]] = style_counts.get(o["style"], 0) + 1
    dom = max(style_counts, key=style_counts.get) if style_counts else ("docx-sup" if doc and doc["kind"] == "docx" else "inline")
    mstyle = a.marker_style if a.marker_style != "auto" else dom
    slots = []  # (unit, pos, order, kind, payload)
    for o in occs:
        slots.append((o["unit"], o["start"], 0, "occ", o))
    insert_at = {}
    added_assessments = {}
    for sid, cids, why, assessment in adds:
        if isinstance(sid, str) and sid.startswith("text:"):  # address a sentence by its words (stable across formats)
            needle = re.sub(r"\s+", "", sid[5:])
            hit = [x for x in sents if needle and needle in re.sub(r"\s+", "", x["plain"])]
            if len(hit) != 1:
                problems.append({"file": "edits", "index": 0, "problem": f"sentence '{sid[5:]}' matched {len(hit)} sentences"})
                continue
            sid = hit[0]["id"]
        s = sent_by_id.get(sid)
        if not s:
            problems.append({"file": "edits", "index": 0, "problem": f"unknown sentence {sid}"})
            continue
        u = doc["units"][s["unit"]]
        already = {c for o in occs if o["sentence"] == sid for c in o["cids"]}
        if already & set(cids):
            changes.append({"kind": "move_target_already_cites", "sentence": sid, "records": sorted(already & set(cids)),
                            "reason": "target sentence already cites this work; not cited a second time"})
            cids = [c for c in cids if c not in already]
            if not cids:
                continue
        if cids:
            changes.append({"kind": "citation_added", "sentence": sid, "records": cids, "evidence": why})
        # merge into an existing marker that already sits at the end of that sentence
        tgt = next((o for o in occs if o["sentence"] == sid and o["end"] >= cite_doc.insertion_point(u["text"], s["start"], s["end"]) - 1
                    and not o.get("narrative")), None)
        locator = {key: assessment[key] for key in ("verdict", "note", "evidence") if assessment.get(key)}
        if locator:
            occurrence_id = tgt["id"] if tgt else f"ins_{sid}"
            added_assessments.setdefault(occurrence_id, {}).update({cid: locator for cid in cids})
        vd = assessment.get("verdict")
        if tgt:
            tgt["cids"] += [c for c in cids if c not in tgt["cids"]]
            continue
        key = (s["unit"], sid)
        if key in insert_at:
            insert_at[key][3] += [c for c in cids if c not in insert_at[key][3]]
        else:
            pos = cite_doc.insertion_point(u["text"], s["start"], s["end"])
            insert_at[key] = [s["unit"], pos, sid, list(cids), vd]
        if vd:
            insert_at[key][4] = vd
    for (ui, sid), (ui2, pos, sid2, cids, vd) in insert_at.items():
        slots.append((ui, pos, 1, "ins", {"cids": cids, "sentence": sid, "unit": ui, "pos": pos, "verdict": vd}))
    slots.sort(key=lambda x: (x[0], x[1], x[2]))
    order, num_of = [], {}
    for ui, pos, _, kind, p in slots:
        for cid in p["cids"]:
            if cid not in num_of:
                num_of[cid] = len(order) + 1
                order.append(cid)
    # ---------------- APA: author-year, year suffixes, alphabetical list
    final = [byid[c] for c in order]
    if style == "apa7":
        groups = {}
        for c in final:
            groups.setdefault((F.author_year_label(dict(c, year_suffix="")), str(c.get("year"))), []).append(c)
        for g in groups.values():
            if len(g) > 1:
                for i, c in enumerate(sorted(g, key=lambda r: title_key(r.get("title")))):
                    c["year_suffix"] = "abcdefghij"[i]
        final = sorted(final, key=lambda r: (title_key(F.apa_authors(r) or r.get("title")), str(r.get("year")), r.get("year_suffix", "")))
    # ---------------- rewrite units
    rs = a.range_sep
    new_units, occ_out = {}, []
    if doc:
        per_unit = {}
        for ui, pos, _, kind, p in slots:
            per_unit.setdefault(ui, []).append((kind, p))
        for ui, items in per_unit.items():
            u = doc["units"][ui]
            ops = []
            for kind, p in items:
                cids = p["cids"]
                if kind == "occ":
                    o = p
                    if o["kind"] == "key" and not numeric:
                        if len(set(cids)) < len(o["keys"]):  # duplicate keys collapsed
                            keys = []
                            for c in cids:
                                k = byid[c].get("bibkey") or next((r.get("bibkey") for r in records if id2c[r["id"]]["id"] == c and r.get("bibkey")), c)
                                if k not in keys:
                                    keys.append(k)
                            new = re.sub(r"\{[^}]*\}$", "{" + ",".join(keys) + "}", o["raw"]) if o["style"] == "latex-cite" else "[" + "; ".join("@" + k for k in keys) + "]"
                        else:
                            new = o["raw"]
                    elif not cids:
                        new = ""
                    elif style == "apa7":
                        if o.get("narrative"):
                            c0 = byid[cids[0]]
                            nm = F.author_year_label(c0).rsplit(", ", 1)
                            new = f"{nm[0]} ({nm[1]})" if not doc.get("zh") else f"{nm[0]}（{nm[1]}）"
                        else:
                            new = F.author_year_marker([byid[c] for c in dict.fromkeys(cids)], zh_text=bool(doc.get("zh") and "（" in o["raw"]))
                    else:
                        st = mstyle if o["kind"] == "num" or mstyle != "docx-sup" else mstyle
                        nums = [num_of[c] for c in cids]
                        new = F.numeric_marker(nums, st, rs)
                        if o.get("narrative"):
                            nm = o["raw"].split("(")[0].split("（")[0].rstrip()
                            new = nm + F.numeric_marker(nums, st, rs)
                    sup = (mstyle == "docx-sup") if doc["kind"] == "docx" else None
                    if numeric and o["kind"] == "num" and o["style"] != mstyle:
                        changes.append({"kind": "marker_style_unified", "occurrence": o["id"], "old": o["raw"], "new": new, "reason": f"{o['style']} -> dominant style {mstyle}"})
                    if o.get("glued") and len(o["nums"]) > 1:
                        changes.append({"kind": "markers_joined", "occurrence": o["id"], "old": o["raw"], "new": new})
                    if new != o["raw"] or (doc["kind"] == "docx" and o["style"] != mstyle and numeric):
                        ops.append((o["start"], o["end"], new, sup))
                    occ_out.append({"id": o["id"], "unit": ui, "sentence": o["sentence"], "role": o["role"], "old": o["raw"], "new": new,
                                    "records": cids, "numbers": [num_of[c] for c in cids] if numeric else None,
                                    "unresolved": o["unresolved"], "support": {c: o["support"].get(c, (None, []))[0] for c in cids},
                                    "matched_terms": {c: o["support"].get(c, (None, []))[1] for c in cids}})
                else:
                    if not cids:
                        continue
                    if style == "apa7":
                        new = F.author_year_marker([byid[c] for c in cids], zh_text=bool(doc.get("zh")))
                        new = " " + new if not doc.get("zh") else new
                    else:
                        new = F.numeric_marker([num_of[c] for c in cids], mstyle, rs)
                        if mstyle == "inline" and not doc.get("zh") and p["pos"] > 0 and u["text"][p["pos"] - 1] != " ":
                            new = " " + new
                    ops.append((p["pos"], p["pos"], new, (mstyle == "docx-sup") if doc["kind"] == "docx" else None))
                    occ_out.append({"id": f"ins_{p['sentence']}", "unit": ui, "sentence": p["sentence"], "role": u["role"], "old": "", "new": new.strip(),
                                    "records": cids, "numbers": [num_of[c] for c in cids] if numeric else None, "unresolved": [],
                                    "support": {c: V.support(sent_by_id[p["sentence"]]["plain"], byid[c])[0] for c in cids}, "inserted": True, "edit_verdict": p.get("verdict")})
            if ops:
                new_units[ui] = cite_doc.tidy(cite_doc.build_unit(u, ops))
    # ---------------- render list
    entries, missing_fields = [], {}
    for n, c in enumerate(final, 1):
        if c.get("placeholder"):
            txt = c["title"]
        elif style == "apa7":
            txt, miss = F.render_apa(c)
            missing_fields[c["id"]] = miss
        else:
            txt, miss = F.render_gbt(c, {"upper": a.upper})
            missing_fields[c["id"]] = miss
        c["number"] = n if numeric else None
        entries.append(txt)
    for cid, miss in missing_fields.items():
        if miss:
            review.append({"type": "missing_fields", "record": cid, "fields": miss, "msg": "target style needs fields that the sources do not give; not invented"})
    uncited = [c for c in canon if c["id"] not in num_of and not c.get("placeholder")]
    if doc:
        uncited_ms = [c for c in uncited if any(m.startswith("M") for m in c["merged_from"])]
        for c in uncited_ms:
            review.append({"type": "uncited_entry_removed", "record": c["id"], "msg": f"reference-list entry never cited in the text; removed from the list: {short(c)}"})
            changes.append({"kind": "entry_removed_uncited", "record": c["id"], "members": c["merged_from"]})
    # claims without citations
    cited_sents = {o["sentence"] for o in occ_out if o["records"]}
    for s in sents:
        if s["role"] in ("body", "appendix") and s["id"] not in cited_sents:
            cue = V.claim_cue(s["plain"])
            if cue:
                review.append({"type": "claim_without_citation", "sentence": s["id"], "cue": cue, "text": s["plain"][:200]})
    # caption citations
    for o in occ_out:
        if o["role"] == "caption" and o["records"]:
            review.append({"type": "caption_citation", "occurrence": o["id"], "msg": "citation sits in a figure/table caption; check that the supported claim is in the caption, not in the body text"})
    # low support hints
    for o in occ_out:
        for c, sc in (o.get("support") or {}).items():
            if sc is not None and sc < 0.12 and not byid[c].get("placeholder"):
                review.append({"type": "weak_lexical_support", "occurrence": o["id"], "record": c, "score": sc, "msg": "sentence shares almost no terms with the cited work: check claim-source match"})
    # ---------------- write outputs
    out = a.out
    stem = os.path.splitext(os.path.basename(a.manuscript))[0] if a.manuscript else "library"
    ext = os.path.splitext(a.manuscript)[1] if a.manuscript else ""
    revised = os.path.join(out, f"{stem}_revised{ext}") if doc else None
    warn = []
    renumber = {}
    if doc:
        for r in records:
            if r.get("origin") == "manuscript_list":
                c = id2c[r["id"]]
                renumber[str(r["label"])] = c.get("number") if c["id"] in num_of else None
        doc["ref_prefix"] = detect_prefix(doc)
        if doc["kind"] == "tex":
            warn = cite_doc.save(doc, new_units, revised, None)
        else:
            warn = cite_doc.save(doc, new_units, revised, entries, ref_prefix=doc["ref_prefix"] if numeric else "")
    ref_txt = os.path.join(out, f"references_{style}.txt")
    write(ref_txt, "\n".join((f"[{i}] " if numeric else "") + e for i, e in enumerate(entries, 1)) + "\n")
    real = [c for c in final if not c.get("placeholder")]
    write(os.path.join(out, "references.bib"), F.render_bibtex(real if doc else canon))
    write(os.path.join(out, "references.ris"), F.render_ris(real if doc else canon))
    write(os.path.join(out, "references.csl.json"), F.render_csl(real if doc else canon))
    lib_out = [{k: v for k, v in c.items() if k not in ("src",)} | {"sources": [x["src"] for x in records if x["id"] in c.get("merged_from", []) and x.get("src")]} for c in canon]
    dump(os.path.join(out, "library_dedup.json"), lib_out)
    dump(os.path.join(out, "merge_log.json"), {"rules": __import__("cite_dedup").__doc__, "pairs": mlog, "clusters": [{"kept": c["id"], "members": c["merged_from"], "field_provenance": c.get("field_provenance")} for c in canon]})
    dump(os.path.join(out, "verification.json"), {"online": a.online, "network": {"requests": net.n, "offline_reason": net.offline_reason, "errors": net.errors[:5]}, "records": verification})
    cmap = []
    for o in occ_out:
        s = sent_by_id.get(o["sentence"], {})
        v = verdicts.get(o["id"]) or ({"verdict": o["edit_verdict"]} if o.get("edit_verdict") else {})
        additions = added_assessments.get(o["id"], {})
        single_addition = additions.get(o["records"][0], {}) if len(o["records"]) == 1 else {}
        mapped = dict(o, sentence_text=s.get("plain"), verdict=v.get("verdict"),
                      verdict_note=v.get("note") or single_addition.get("note"),
                      evidence=v.get("evidence") or single_addition.get("evidence"),
                      references=[{"record": c, "number": num_of.get(c) if numeric else None, "text": short(byid[c]), "doi": byid[c].get("doi")}
                                  for c in o["records"]],
                      # "record_metadata" = verdict made from the library/list record only; "pdf" = source PDF text was supplied
                      evidence_basis="pdf" if inv.get("pdfs") else "record_metadata")
        if additions:
            mapped["added_record_assessments"] = additions
        cmap.append(mapped)
    dump(os.path.join(out, "citation_map.json"), cmap)
    dump(os.path.join(out, "renumber_map.json"), {"old_label_to_new_number": renumber, "order_rule": "first appearance in body text incl. captions/appendix (GB/T 7714-2015 顺序编码制)" if numeric else "author-year (no numbers)"})
    # diff
    diff_path = None
    if doc and doc["kind"] != "docx":
        old = read_text(a.manuscript).replace("\r\n", "\n").splitlines()
        new = read_text(revised).replace("\r\n", "\n").splitlines()
        diff_path = os.path.join(out, "manuscript.diff")
        write(diff_path, "\n".join(difflib.unified_diff(old, new, "original", "revised", lineterm="", n=0)) + "\n")
    elif doc:
        diff_path = os.path.join(out, "manuscript_changes.md")
        L = ["# Changed paragraphs (docx)", ""]
        for ui, pcs in sorted(new_units.items()):
            L += [f"## unit {ui}", "- before: " + doc["units"][ui]["text"], "- after:  " + "".join(p[0] for p in pcs), ""]
        write(diff_path, "\n".join(L))
    # consistency check on the written manuscript
    chk = check_manuscript(revised, style) if (doc and numeric and doc["kind"] != "tex") else None
    previews = render_preview(revised, out) if (doc and doc["kind"] == "docx" and not a.no_preview) else []
    # result
    for r in review:  # a bad source that is no longer cited does not block the result
        if r.get("record") and r["type"].startswith("source_") and r["record"] not in num_of:
            r["resolved"] = "record no longer cited after edits"
    final_by_id = {row["id"]: row for row in cmap}
    for item in review:
        if item["type"] == "orphan_citation" and all(
                item["marker"] not in {str(value) for value in final_by_id.get(oid, {}).get("unresolved", [])}
                for oid in item["occurrences"]):
            item["resolved"] = "original marker replaced or removed"
    needs = [r for r in review if not r.get("resolved") and r["type"] in ("orphan_citation", "source_not_found", "source_doi_not_found", "source_mismatch", "dedup_conflict")]
    unjudged = [o["id"] for o in occ_out if o["records"] and o["id"] not in verdicts and not o.get("edit_verdict")]
    status = "complete"
    reasons = []
    if needs:
        status, _ = "partial", reasons.append(f"{len(needs)} blocking item(s) need human confirmation")
    if chk and not chk["ok"]:
        status, _ = "partial", reasons.append("post-write consistency check failed: " + "; ".join(chk["errors"][:3]))
    removed = [c for c in changes if c["kind"] == "citation_removed"]
    if removed:
        status, _ = "partial", reasons.append(f"{len(removed)} citation(s) removed by edit; the sentence(s) need a real source or rewording (human)")
    if unjudged:
        status, _ = "partial", reasons.append(f"{len(unjudged)} citation occurrence(s) without a claim-source verdict (fill edits.occurrences.*.verdict)")
    if a.clean:
        if not a.online:
            offline_cited = [record["id"] for record in final if record["id"] in verification]
            if offline_cited:
                review.append({"type": "registry_not_checked", "records": offline_cited,
                               "msg": "Registry checks were disabled. See verification.json for per-record metadata checks and citation_map.json for claim evidence."})
        for occurrence in cmap:
            if occurrence["verdict"] in ("partial", "mismatch", "unverifiable") or not occurrence["verdict"]:
                item = {"type": "claim_source_review", "occurrence": occurrence["id"], "sentence": occurrence["sentence"],
                        "verdict": occurrence["verdict"],
                        "msg": occurrence["verdict_note"] or "claim-source match needs confirmation"}
                if occurrence["evidence"]:
                    item["evidence"] = occurrence["evidence"]
                review.append(item)
        open_types = {"claim_source_review", "claim_without_citation", "source_unconfirmed", "case_input", "invalid_edits", "replacement_not_applied", "insertion_not_applied", "pdf_text_conversion"}
        if doc and doc["kind"] == "docx" and not a.no_preview and not previews:
            review.append({"type": "preview_missing", "msg": "DOCX preview renderer did not produce a PDF"})
            open_types.add("preview_missing")
        if problems or any(item["type"] in open_types and not item.get("resolved") for item in review):
            status, _ = "partial", reasons.append("see review.md for unresolved source, input or editing items")
    if not a.online:
        reasons.append("sources not checked online (offline run)")
    if warn:
        reasons.append("; ".join(warn[:2]))
    summary = {"records_in": len(records), "records_after_dedup": len([c for c in canon if not c.get("placeholder")]), "merged_clusters": sum(1 for c in canon if len(c.get("merged_from", [])) > 1),
               "occurrences": len(occs), "occurrences_out": len(occ_out), "references_out": len(final), "orphans": len(orphans),
               "uncited_removed": sum(1 for c in changes if c["kind"] == "entry_removed_uncited"), "auto_moves": sum(1 for m in moves if m["auto"]),
               "placement_suggestions": sum(1 for m in moves if not m["auto"]), "verified": sum(1 for v in verification.values() if v["status"].startswith("verified")),
               "verification_status_counts": count([v["status"] for v in verification.values()]), "review_items": len(review),
               "review_by_type": count([r["type"] for r in review]), "parse_problems": len(problems), "seconds": round(time.time() - t0, 2)}
    res_path = os.path.join(out, "result.json")
    res = base_result(a.case_id, a.contract)
    res.update({"case_id": a.case_id, "tool": f"cite-sync {VERSION}", "status": status, "status_reason": reasons,
                "style": style, "marker_style": mstyle if numeric else "author-year",
                "artifacts": {k: v for k, v in {"revised_manuscript": revised, "references": ref_txt, "bibtex": os.path.join(out, "references.bib"),
                                                "ris": os.path.join(out, "references.ris"), "csl_json": os.path.join(out, "references.csl.json"),
                                                "citation_map": os.path.join(out, "citation_map.json"), "merge_log": os.path.join(out, "merge_log.json"),
                                                "verification": os.path.join(out, "verification.json"), "renumber_map": os.path.join(out, "renumber_map.json"),
                                                "library_dedup": os.path.join(out, "library_dedup.json"), "diff": diff_path, "review": os.path.join(out, "review.md"),
                                                "previews": previews or None}.items() if v},
                "summary": summary, "consistency_check": chk, "references_list": [(f"[{i}] " if numeric else "") + e for i, e in enumerate(entries, 1)],
                "changes": changes, "needs_review": review, "parse_problems": problems,
                "inputs": {"case": a.case, "evidence_pdfs": inv.get("pdfs", []), "manuscript": fi(original_manuscript) if original_manuscript else None, "libraries": [fi(p) for p in a.library or [] if os.path.exists(p)]},
                "edits_applied": a.edits if edits else None,
                "uncertainty": "Claim-source verdicts come from the agent reading sentence + reference metadata (and PDFs when given); lexical support scores are hints only. "
                               + ("Online metadata from Crossref/arXiv may itself be incomplete (e.g. shortened author lists)." if a.online else "No online verification in this run.")})
    res["unmapped_contract_fields"] = fill_contract(res, a.contract, a.work, {
        "citation_map": cmap, "verification": verification, "renumber_map": renumber, "library_dedup": lib_out, "merge_log": mlog,
    })
    if a.clean and res["unmapped_contract_fields"]:
        res["status"] = status = "partial"
        reasons.append("some contract fields need confirmation or a case-specific override")
    save_result(out, res, a.contract, a.clean)
    if a.clean:
        write(os.path.join(a.work, "priority_review.md"), priority_review(review, cmap, canon, inv.get("pdfs", [])))
    write(os.path.join(out, "review.md"), review_md(res, cmap, verification, byid, numeric, moves))
    dump(os.path.join(a.work, "edits_template.json"), edits_template(occ_out, sent_by_id, byid, num_of, numeric, edits))
    write(os.path.join(a.work, "claim_matrix.md"), claim_matrix(occ_out, sent_by_id, byid, num_of, numeric, review))
    print(json.dumps({"status": status, "status_reason": reasons, "summary": summary, "result": res_path,
                      "claim_matrix": os.path.join(a.work, "claim_matrix.md"), "edits_template": os.path.join(a.work, "edits_template.json")}, ensure_ascii=False, indent=1))


def count(xs):
    d = {}
    for x in xs:
        d[x] = d.get(x, 0) + 1
    return d


def detect_prefix(doc):
    for _, t in cite_doc.reflist_lines(doc):
        s = t.strip()
        if re.match(r"^\[\d+\]", s):
            return "[{n}] "
        if re.match(r"^\d+\.\s", s):
            return "{n}. "
        if re.match(r"^［\d+］", s):
            return "［{n}］"
    return "[{n}] "


def fill_contract(res, fields, work, structured):
    artifact = res["artifacts"]
    overrides = os.path.join(work, "contract_overrides.json")
    try:
        custom = jload(overrides) if os.path.isfile(overrides) else {}
    except (ValueError, OSError):
        custom = {}
    aliases = (
        (r"preview|pdf|png|预览", "previews"), (r"renumber|重编号", "renumber_map"),
        (r"dedup|去重", "library_dedup"), (r"merge|合并", "merge_log"),
        (r"verif|核验", "verification"), (r"citation|claim|evidence|source_map|引文|论断|证据|引用", "citation_map"),
        (r"diff", "diff"), (r"bibtex|references_bib", "bibtex"),
        (r"^ris$|references_ris", "ris"), (r"csl", "csl_json"),
        (r"manuscript|draft|revised|paper|稿", "revised_manuscript"),
        (r"bibliograph|references?|文献|ref_list", "references"),
    )
    missing = []
    for field, spec in fields.items():
        if field in ("case_id", "status"):
            continue
        if isinstance(custom, dict) and field in custom:
            res[field] = custom[field]
            continue
        if res.get(field) is not None:
            continue
        kind = spec.get("type", "") if isinstance(spec, dict) else str(spec or "")
        name = next((key for pattern, key in aliases if re.search(pattern, field, re.I)), None)
        if re.search(r"review|confirm|question|人工|确认|issue", field, re.I):
            value = res["needs_review"]
        elif name == "references":
            value = artifact.get(name) if "path" in kind.lower() or re.search(r"file|path", field, re.I) else res["references_list"]
        elif name == "previews":
            vals = artifact.get(name) or []
            ext = next((ext for ext in (".pdf", ".png") if ext[1:] in field.lower()), None)
            vals = [path for path in vals if ext is None or path.endswith(ext)]
            value = vals if kind in ("array", "list") or field.endswith("s") else next(iter(vals), None)
        elif kind in ("array", "list", "object", "dict") and name in structured:
            value = structured[name]
        elif name:
            value = artifact.get(name)
        elif re.search(r"change|revision|修改", field, re.I):
            value = res["changes"]
        elif re.search(r"consisten|一致", field, re.I):
            value = res["consistency_check"]
        else:
            value = None
        res[field] = value
        if value is None:
            missing.append(field)
    return missing


def priority_review(review, occurrences, records, pdfs):
    issues = [(item.get("sentence"), item.get("text"), set()) for item in review if item["type"] == "claim_without_citation"]
    suspect = {item.get("occurrence") for item in review if item["type"] in ("weak_lexical_support", "replacement_not_applied")}
    bad = {item.get("record") for item in review if item["type"] in ("source_mismatch", "source_not_found", "source_doi_not_found")}
    for item in occurrences:
        claim = item["sentence_text"] or ""
        cited = set(item["records"])
        score = max((value or 0 for value in item.get("support", {}).values()), default=0)
        stronger = score < 0.45 and any(
            V.support(claim, record)[0] >= max(0.45, score + 0.25)
            for record in records if record["id"] not in cited and not record.get("placeholder"))
        if stronger or item["id"] in suspect or item["unresolved"] or bad.intersection(cited):
            issues.append((item["id"], claim, cited))
    lines = ["# Priority citation review", "", "Candidate matches are retrieval hints. Confirm the actual source passage before editing.", ""]
    if pdfs:
        lines += ["## Supplied PDF sources", ""] + [f"- {path}" for path in pdfs] + [""]
    for locator, claim, current in issues:
        if not claim:
            continue
        lines += [f"## {locator}", "", f"> {claim}", ""]
        ranked = []
        for record in records:
            if record["id"] in current or record.get("placeholder"):
                continue
            score, terms = V.support(claim, record)
            if score >= 0.18:
                ranked.append((score, record["id"], record, terms))
        for score, rid, record, terms in sorted(ranked, key=lambda row: (-row[0], row[1]))[:3]:
            lines.append(f"- {rid}: {short(record)} | terms {', '.join(terms)} | {record.get('doi') or record.get('url') or ''}")
        if not ranked:
            lines.append("- No indexed candidate. Inspect supplied sources or leave this item for review.")
        lines.append("")
    return "\n".join(lines)


def review_md(res, cmap, ver, byid, numeric, moves):
    L = [f"# cite-sync review - case {res.get('case_id')}", "", f"status: **{res['status']}**  ", "reasons: " + ("; ".join(res["status_reason"]) or "-"), "",
         "## Summary", "```", json.dumps(res["summary"], ensure_ascii=False, indent=1), "```", ""]
    if res.get("consistency_check"):
        c = res["consistency_check"]
        L += ["## Numbering / list consistency (re-parsed from the written file)", f"ok = {c['ok']}; markers use 1..{c['max_number']}; list entries {c['list_entries']}",
              *[f"- error: {e}" for e in c["errors"]], *[f"- warning: {e}" for e in c["warnings"]], ""]
    L += ["## Items that need a human decision", ""]
    for r in res["needs_review"]:
        L.append(f"- **{r['type']}** " + " ".join(f"{k}={v}" for k, v in r.items() if k not in ("type", "details")))
    L += ["", "## Changes", ""]
    for c in res["changes"]:
        L.append("- " + json.dumps(c, ensure_ascii=False))
    L += ["", "## Source verification", "", "| record | status | issues | corrections |", "|-|-|-|-|"]
    for rid, v in ver.items():
        L.append(f"| {rid} {v['record'][:50]} | {v['status']} | {'; '.join(i['code'] for i in v['issues'])} | {', '.join(v['corrections'])} |")
    L += ["", "## Citation occurrences", "", "| occ | sentence | marker old -> new | records | support | verdict | evidence / review note |", "|-|-|-|-|-|-|-|"]
    for o in cmap:
        notes = [o["evidence"], o["verdict_note"]]
        if len(o["records"]) > 1:
            notes.extend(f"{rid}: {assessment['evidence']}" for rid, assessment in o.get("added_record_assessments", {}).items()
                         if assessment.get("evidence"))
        evidence = " / ".join(dict.fromkeys(" ".join(str(note).split()).replace("|", r"\|") for note in notes if note))
        L.append(f"| {o['id']} | {(o.get('sentence_text') or '')[:70]} | `{o['old']}` -> `{o['new']}` | {', '.join(o['records'])} | {o['support']} | {o.get('verdict') or '-'} | {evidence or '-'} |")
    return "\n".join(L) + "\n"


def edits_template(occ_out, sent_by_id, byid, num_of, numeric, edits):
    occ = {}
    for o in occ_out:
        prev = (edits.get("occurrences") or {}).get(o["id"], {})
        occ[o["id"]] = {"sentence": (sent_by_id.get(o["sentence"]) or {}).get("plain", "")[:160], "refs": o["records"],
                        "verdict": prev.get("verdict"), "note": prev.get("note", ""), "action": prev.get("action", "keep")}
    return {"_help": "verdict: supported | partial | mismatch | unverifiable. action: keep | remove | replace (refs) | drop_refs (refs). "
                     "move_to: sentence id (optionally move_refs). add_citations: [{sentence, refs, note}]. record_overrides: {record_id: {field: value, _source: '...'}}. "
                     "force_merge / forbid_merge: [[id, id]]. Re-run `cite.py run ... --edits <this file>`.",
            "occurrences": occ, "add_citations": edits.get("add_citations", []), "record_overrides": edits.get("record_overrides", {}),
            "force_merge": edits.get("force_merge", []), "forbid_merge": edits.get("forbid_merge", [])}


def claim_matrix(occ_out, sent_by_id, byid, num_of, numeric, review):
    L = ["# Claim-citation matrix (judge every row; write verdicts into edits.json)", "",
         "Columns: occurrence | sentence (markers removed) | cited record (title / venue / year) | lexical support hint", ""]
    for o in occ_out:
        s = (sent_by_id.get(o["sentence"]) or {}).get("plain", "")
        L.append(f"## {o['id']}  ({o['sentence']}, {o['role']})  `{o['old']}` -> `{o['new']}`")
        L.append(f"> {s}")
        for c in o["records"]:
            r = byid[c]
            L.append(f"- {c} [{num_of.get(c) if numeric else ''}] {r.get('title')} | {r.get('title_alt') or ''} | {r.get('container') or r.get('publisher') or ''} {r.get('year') or ''} | support={o['support'].get(c)} terms={o.get('matched_terms', {}).get(c)}")
            if r.get("abstract"):
                L.append(f"  - abstract: {r['abstract'][:300]}")
        L.append("")
    cues = [r for r in review if r["type"] == "claim_without_citation"]
    if cues:
        L += ["# Sentences that look like claims but carry no citation", ""]
        L += [f"- {r['sentence']} (cue: {r['cue']}): {r['text']}" for r in cues]
    return "\n".join(L) + "\n"


def render_preview(path, out):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        for p in (r"C:\Program Files\LibreOffice\program\soffice.exe", "/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice"):
            if os.path.exists(p):
                exe = p
    pdf = os.path.join(out, os.path.splitext(os.path.basename(path))[0] + ".pdf")
    rendered = False
    if exe:
        try:
            with tempfile.TemporaryDirectory(dir=out) as rendering:
                command = [exe, "--headless", "--convert-to", "pdf", "--outdir", rendering, os.path.abspath(path)]
                subprocess.run(command, capture_output=True, timeout=25, check=True)
                converted = os.path.join(rendering, os.path.basename(pdf))
                if os.path.isfile(converted):
                    os.replace(converted, pdf)
                    rendered = True
        except (OSError, subprocess.SubprocessError):
            pass
    if not rendered:
        try:
            from html import escape
            from io import BytesIO
            import pymupdf as fitz
            doc = cite_doc.load(path)
            html = "".join("<p>" + escape(unit["text"]) + "</p>" for unit in doc["units"] if unit["text"].strip())
            story = fitz.Story(html=html, user_css="body {font-size: 11pt;} p {margin-bottom: 0.45em;}")
            page = fitz.paper_rect("a4")
            with tempfile.TemporaryDirectory(dir=out) as rendering:
                generated = os.path.join(rendering, os.path.basename(pdf))
                buffer = BytesIO()
                writer = fitz.DocumentWriter(buffer)
                more = True
                while more:
                    device = writer.begin_page(page)
                    more, _ = story.place(page + (48, 48, -48, -48))
                    story.draw(device)
                    writer.end_page()
                writer.close()
                with open(generated, "wb") as stream:
                    stream.write(buffer.getvalue())
                os.replace(generated, pdf)
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            log(f"DOCX preview unavailable: {exc}")
            return []
    res = [pdf] if os.path.exists(pdf) else []
    try:
        import pymupdf as fitz
        d = fitz.open(pdf)
        for i, pg in enumerate(d):
            if i >= 3:
                break
            png = pdf[:-4] + f"_p{i + 1}.png"
            pg.get_pixmap(dpi=80).save(png)
            res.append(png)
    except Exception:
        pass
    return res


def fail(a, reason, problems):
    report_path = os.path.join(a.out, "run_report.json")
    previous = a.previous
    if os.path.isfile(report_path):
        try:
            saved = jload(report_path)
            if isinstance(saved, dict) and saved.get("case_id") == a.case_id:
                previous = saved
        except (OSError, ValueError):
            pass
    if not previous.get("artifacts") and not a.previous.get("artifacts"):
        report = base_result(a.case_id, a.contract)
        report.update(status="failed", status_reason=[reason], parse_problems=problems)
        save_result(a.out, report, a.contract, a.clean)
    print(json.dumps({"status": "failed", "reason": reason, "parse_problems": problems}, ensure_ascii=False, indent=1))
    sys.exit(2)


# ---------------------------------------------------------------- check
def check_manuscript(path, style="gbt7714"):
    """Re-parse a numbered manuscript and check body markers vs list: continuity, order, coverage."""
    doc = cite_doc.load(path)
    occs, _ = cite_doc.analyse(doc)
    nums = [n for o in occs if o["kind"] == "num" for n in o["nums"]]
    entries = split_reflist([t for _, t in cite_doc.reflist_lines(doc)])
    labels = [n for n, _ in entries]
    errors, warnings = [], []
    if doc["ref_start"] is None:
        errors.append("no reference list heading found")
    first = []
    for n in nums:
        if n not in first:
            first.append(n)
    if first != sorted(first):
        bad = next(i for i in range(len(first)) if first[i] != sorted(first)[i])
        errors.append(f"numbers not in order of first appearance (first deviation at citation #{bad + 1}: {first[bad]})")
    mx = max(nums) if nums else 0
    if first and sorted(first) != list(range(1, mx + 1)):
        errors.append(f"cited numbers not continuous: missing {sorted(set(range(1, mx + 1)) - set(first))}")
    if labels != list(range(1, len(labels) + 1)):
        errors.append(f"list labels not 1..N: {labels[:20]}")
    if len(entries) != mx:
        errors.append(f"list has {len(entries)} entries but text cites up to [{mx}]")
    over = sorted({n for n in nums if n > len(entries)})
    if over:
        errors.append(f"text cites numbers without list entry: {over}")
    uncited = sorted(set(range(1, len(entries) + 1)) - set(nums))
    if uncited:
        errors.append(f"list entries never cited: {uncited}")
    styles = count([o["style"] for o in occs if o["kind"] == "num"])
    if len(styles) > 1:
        warnings.append(f"mixed marker styles {styles}")
    keys = [title_key(t)[:80] for _, t in entries]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        errors.append(f"{len(dup)} identical list entries")
    dois = [norm_doi(m.group(1)) for _, t in entries for m in [re.search(r"(10\.\d{4,9}/[^\s,;]+)", t)] if m]
    if len(dois) != len(set(dois)):
        errors.append("two list entries share a DOI")
    for o in occs:
        if o["kind"] == "num" and len(o["nums"]) != len(set(o["nums"])):
            warnings.append(f"repeated number inside one marker {o['raw']}")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "max_number": mx, "list_entries": len(entries),
            "markers": len(occs), "marker_styles": styles}


def cmd_check(a):
    r = check_manuscript(a.manuscript, a.style)
    print(json.dumps(r, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- convert
def cmd_convert(a):
    recs, probs = [], []
    for li, lp in enumerate(a.library):
        rs, ps, _ = load_library(lp)
        for r in rs:
            r["id"] = f"L{li + 1}-{r['src']['index']}"
        recs += rs
        probs += ps
    log_ = []
    if a.dedup:
        recs, log_, _ = dedup(recs)
    if a.online:
        net = V.Net(os.path.join(os.path.dirname(os.path.abspath(a.out)), "net_cache.json"), True)
        for r in recs:
            st, det, corr = V.online_check(net, r)
            for f, (old, new, src) in corr.items():
                r[f] = new
            r["verification"] = st
        net.save()
    if a.to in ("gbt7714", "apa7"):
        fn = F.render_gbt if a.to == "gbt7714" else F.render_apa
        rows = [fn(r)[0] for r in recs]
        text = "\n".join(f"[{i}] {t}" if a.to == "gbt7714" else t for i, t in enumerate(rows, 1)) + "\n"
    elif a.to == "bibtex":
        text = F.render_bibtex(recs)
    elif a.to == "ris":
        text = F.render_ris(recs)
    else:
        text = F.render_csl(recs)
    write(a.out, text)
    print(json.dumps({"records": len(recs), "problems": probs, "merges": [e for e in log_ if e["merged"]], "out": a.out}, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    i = sp.add_parser("init")
    i.add_argument("--case", required=True)
    i.add_argument("--out", required=True)
    i.add_argument("--work", required=True)
    r = sp.add_parser("run")
    r.add_argument("--case", help="Detect case inputs and honor output_contract")
    r.add_argument("--manuscript")
    r.add_argument("--library", action="append")
    r.add_argument("--style", choices=["gbt7714", "apa7"])
    r.add_argument("--marker-style", default="auto", choices=["auto", "inline", "pandoc-sup", "html-sup", "latex-sup", "docx-sup"])
    r.add_argument("--range-sep", default="-")
    r.add_argument("--upper", action="store_true", help="GB/T: upper-case Western family names")
    r.add_argument("--online", action="store_true")
    r.add_argument("--net-budget", type=int, default=300, help="total seconds for all registry requests")
    r.add_argument("--net-timeout", type=int, default=20, help="seconds per registry request")
    r.add_argument("--net-max-requests", type=int, default=60)
    r.add_argument("--no-apply-corrections", dest="apply_corrections", action="store_false")
    r.add_argument("--no-auto-move", dest="auto_move", action="store_false")
    r.add_argument("--no-preview", action="store_true")
    r.add_argument("--edits")
    r.add_argument("--case-id")
    r.add_argument("--out", required=True)
    r.add_argument("--work", required=True)
    c = sp.add_parser("check")
    c.add_argument("--manuscript", required=True)
    c.add_argument("--style", default="gbt7714")
    v = sp.add_parser("convert")
    v.add_argument("--library", action="append", required=True)
    v.add_argument("--to", required=True, choices=["gbt7714", "apa7", "bibtex", "ris", "csl"])
    v.add_argument("--dedup", action="store_true")
    v.add_argument("--online", action="store_true")
    v.add_argument("--out", required=True)
    a = p.parse_args()
    {"init": cmd_init, "run": cmd_run, "check": cmd_check, "convert": cmd_convert}[a.cmd](a)


if __name__ == "__main__":
    main()
