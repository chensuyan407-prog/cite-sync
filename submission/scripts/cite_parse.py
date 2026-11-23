"""Library parsers: BibTeX, RIS, EndNote/Refer (.enw, CNKI EndNote export), NoteExpress (CNKI .net),
CSL-JSON, and free-text numbered reference lists (GB/T 7714 / APA / Vancouver-like).

Every parser returns (records, problems). A problem is {"file", "index", "problem", "raw"}; a broken entry
never stops the other entries from loading.
"""
import json
import os
import re

from cite_common import (has_cjk, nfkc, norm_arxiv, norm_doi, read_text, split_name)

BIB_TYPE = {"article": "article-journal", "inproceedings": "paper-conference", "conference": "paper-conference",
            "proceedings": "book", "book": "book", "incollection": "chapter", "inbook": "chapter",
            "phdthesis": "thesis", "mastersthesis": "thesis", "thesis": "thesis", "techreport": "report",
            "report": "report", "misc": "misc", "online": "webpage", "electronic": "webpage", "www": "webpage",
            "unpublished": "misc", "standard": "standard", "patent": "patent", "dataset": "dataset"}
RIS_TYPE = {"JOUR": "article-journal", "JFULL": "article-journal", "MGZN": "article-journal", "CONF": "paper-conference",
            "CPAPER": "paper-conference", "BOOK": "book", "CHAP": "chapter", "THES": "thesis", "RPRT": "report",
            "ELEC": "webpage", "WEB": "webpage", "STAND": "standard", "PAT": "patent", "DATA": "dataset",
            "UNPB": "preprint", "GEN": "misc"}
ENW_TYPE = {"journal article": "article-journal", "conference paper": "paper-conference",
            "conference proceedings": "paper-conference", "book": "book", "book section": "chapter",
            "thesis": "thesis", "report": "report", "electronic article": "webpage", "web page": "webpage",
            "standard": "standard", "patent": "patent", "dataset": "dataset", "generic": "misc",
            "期刊文章": "article-journal", "会议论文": "paper-conference", "学位论文": "thesis", "图书": "book",
            "报告": "report", "专利": "patent", "标准": "standard", "报纸文章": "article-journal"}
LATEX_ACC = {r"\"a": "ä", r"\"o": "ö", r"\"u": "ü", r"\'e": "é", r"\'a": "á", r"\`e": "è", r"\^o": "ô",
             r"\~n": "ñ", r"\c c": "ç", r"\'o": "ó", r"\'i": "í", r"\ss": "ß", r"\aa": "å", r"\o": "ø"}


def _delatex(s):
    s = s or ""
    for k, v in LATEX_ACC.items():
        s = s.replace("{" + k + "}", v).replace(k, v)
    s = re.sub(r"\\(textit|textbf|emph|mathrm|text)\{([^{}]*)\}", r"\2", s)
    s = s.replace("\\&", "&").replace("--", "–").replace("~", " ")
    s = re.sub(r"\{?\\L\}?", "Ł", s)
    s = re.sub(r"\{?\\l\}?(?=[a-z])", "ł", s)
    s = re.sub(r"\\[A-Za-z]+\s*", "", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def split_authors(s, sep=None):
    s = nfkc(s or "").strip()
    if not s:
        return []
    if sep:
        parts = re.split(sep, s)
    elif " and " in s:
        parts = s.split(" and ")
    elif re.search(r"[;；]", s):
        parts = re.split(r"[;；]", s)
    elif has_cjk(s):
        parts = re.split(r"[,，、]", s)
    else:
        parts = [s]
    out = []
    for p in parts:
        a = split_name(p)
        if a:
            out.append(a)
    return out


def _pages(sp, ep=None):
    sp = nfkc(sp or "").strip().replace("--", "-").replace("–", "-").replace("—", "-")
    if ep:
        ep = nfkc(ep).strip()
        return f"{sp}-{ep}" if sp and ep and ep != sp else sp
    return sp


def _finish(r):
    r["doi"] = norm_doi(r.get("doi"))
    if not r.get("arxiv"):
        for k in ("eprint", "url", "note", "container", "doi"):
            v = r.get(k) or ""
            if "arxiv" in v.lower() or (k == "eprint" and v):
                a = norm_arxiv(v.split("arxiv.org/abs/")[-1] if "arxiv.org" in v else v.split(":")[-1].strip())
                if a:
                    r["arxiv"] = a
                    break
    m = re.match(r"^10\.48550/arxiv\.(.+)$", r.get("doi") or "")
    if m and not r.get("arxiv"):
        r["arxiv"] = norm_arxiv(m.group(1))
    if r.get("year"):
        m = re.search(r"(1[5-9]\d\d|20\d\d)", str(r["year"]))
        r["year"] = m.group(1) if m else str(r["year"])
    for k in ("title", "title_alt", "container"):
        if r.get(k):
            r[k] = re.sub(r"\s+", " ", nfkc(r[k])).strip().rstrip(".")
    r["lang"] = "zh" if has_cjk(r.get("title")) else "en"
    if r.get("container") and re.search(r"^arxiv|arxiv preprint|biorxiv|medrxiv|preprint", r["container"], re.I) and r.get("type") in ("article-journal", "misc", None):
        r["type"] = "preprint"
    if r.get("type") not in (None, "preprint") and r.get("arxiv") and not r.get("container"):
        r["type"] = "preprint"
    r.setdefault("type", "misc")
    r.pop("eprint", None)
    return {k: v for k, v in r.items() if v not in (None, "", [])}


# ---------------------------------------------------------------- BibTeX
def parse_bibtex(text, fname=""):
    recs, probs = [], []
    i, n, idx = 0, len(text), 0
    while True:
        m = re.compile(r"@(\w+)\s*([{(])", re.S).search(text, i)
        if not m:
            break
        typ = m.group(1).lower()
        start = m.end()
        depth, j = 1, start
        while j < n and depth:
            if text[j] in "{(":
                depth += 1
            elif text[j] in "})":
                depth -= 1
            j += 1
        body = text[start:j - 1]
        i = j
        if typ in ("comment", "preamble", "string"):
            continue
        idx += 1
        raw = text[m.start():j]
        if depth:
            probs.append({"file": fname, "index": idx, "problem": "unbalanced braces (entry truncated?)", "raw": raw[:300]})
            continue
        key, _, rest = body.partition(",")
        fields = {}
        k = 0
        while k < len(rest):
            fm = re.compile(r"\s*([\w\-:]+)\s*=\s*", re.S).match(rest, k)
            if not fm:
                k += 1
                continue
            name = fm.group(1).lower()
            k = fm.end()
            if k < len(rest) and rest[k] == "{":
                d, s = 1, k + 1
                k += 1
                while k < len(rest) and d:
                    d += {"{": 1, "}": -1}.get(rest[k], 0)
                    k += 1
                val = rest[s:k - 1]
            elif k < len(rest) and rest[k] == '"':
                s = k + 1
                k = rest.find('"', s)
                k = len(rest) if k < 0 else k
                val = rest[s:k]
                k += 1
            else:
                vm = re.compile(r"[^,]*").match(rest, k)
                val = vm.group(0).strip()
                k = vm.end()
            fields[name] = val
        if not fields:
            probs.append({"file": fname, "index": idx, "problem": "no fields parsed", "raw": raw[:300]})
            continue
        f = {k: _delatex(v) for k, v in fields.items()}
        r = {"bibkey": key.strip(), "type": BIB_TYPE.get(typ, "misc"), "title": f.get("title"),
             "authors": split_authors(f.get("author", "")) if f.get("author") else [],
             "editors": split_authors(f.get("editor", "")) if f.get("editor") else [],
             "year": f.get("year") or f.get("date", "")[:4],
             "container": f.get("journal") or f.get("journaltitle") or f.get("booktitle"),
             "volume": f.get("volume"), "issue": f.get("number") or f.get("issue"), "pages": _pages(f.get("pages")),
             "publisher": f.get("publisher") or f.get("school") or f.get("institution") or f.get("organization"),
             "place": f.get("address") or f.get("location"), "edition": f.get("edition"), "doi": f.get("doi"),
             "isbn": f.get("isbn"), "url": f.get("url"), "accessed": f.get("urldate"), "abstract": f.get("abstract"),
             "keywords": [x.strip() for x in re.split(r"[;,，；]", f.get("keywords", "")) if x.strip()],
             "eprint": f.get("eprint") if (f.get("archiveprefix", "").lower() == "arxiv" or f.get("eprinttype", "").lower() == "arxiv") else None,
             "note": f.get("note"), "title_alt": f.get("title_alt") or f.get("translatedtitle") or f.get("origtitle") or f.get("title_en") or f.get("title_zh"),
             "src": {"file": fname, "index": idx, "format": "bibtex", "raw": raw[:1500]}}
        if r["type"] == "misc" and r.get("container") and re.search(r"arxiv|preprint", r["container"], re.I):
            r["type"] = "preprint"
        if not r.get("title"):
            probs.append({"file": fname, "index": idx, "problem": "entry has no title", "raw": raw[:300]})
        recs.append(_finish(r))
    if not recs and text.strip() and "@" not in text:
        probs.append({"file": fname, "index": 0, "problem": "no BibTeX entries found", "raw": text[:200]})
    return recs, probs


# ---------------------------------------------------------------- RIS
def parse_ris(text, fname=""):
    recs, probs, cur, idx = [], [], None, 0
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  -\s?(.*)$", line)
        if not m:
            if cur is not None and line.strip() and cur.get("_last"):
                cur[cur["_last"]][-1] += " " + line.strip()
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            idx += 1
            cur = {"TY": [val], "_raw": [line]}
            continue
        if cur is None:
            continue
        cur["_raw"].append(line)
        if tag == "ER":
            recs.append(_ris_rec(cur, fname, idx, probs))
            cur = None
            continue
        cur.setdefault(tag, []).append(val)
        cur["_last"] = tag
    if cur is not None:
        probs.append({"file": fname, "index": idx, "problem": "RIS record without ER (file truncated?) - kept", "raw": "\n".join(cur["_raw"])[:300]})
        recs.append(_ris_rec(cur, fname, idx, probs))
    return recs, probs


def _ris_rec(c, fname, idx, probs):
    g = lambda *tags: next((c[t][0] for t in tags if c.get(t)), None)
    authors = []
    for t in ("AU", "A1"):
        for a in c.get(t, []):
            authors += [split_name(a)] if not re.search(r"[;；]", a) else split_authors(a)
    typ = RIS_TYPE.get(g("TY") or "", "misc")
    r = {"type": typ, "title": g("TI", "T1", "CT"), "title_alt": g("TT", "ST") if g("TT") else None,
         "authors": [a for a in authors if a], "year": g("PY", "Y1", "DA"),
         "container": g("T2", "JO", "JF", "BT", "JA") if typ != "book" else g("T2"),
         "volume": g("VL"), "issue": g("IS"), "pages": _pages(g("SP"), g("EP")), "publisher": g("PB"), "place": g("CY"),
         "doi": g("DO") or (g("M3") if norm_doi(g("M3")) else None), "isbn": g("SN") if typ in ("book", "chapter") else None,
         "url": g("UR"), "abstract": g("AB", "N2"), "keywords": c.get("KW", []), "accessed": g("Y2"), "note": g("N1"),
         "src": {"file": fname, "index": idx, "format": "ris", "raw": "\n".join(c["_raw"])[:1500]}}
    if not r["title"]:
        probs.append({"file": fname, "index": idx, "problem": "RIS record has no TI/T1", "raw": "\n".join(c["_raw"])[:300]})
    return _finish(r)


# ---------------------------------------------------------------- EndNote / Refer (%A ...) incl. CNKI export
def parse_endnote(text, fname=""):
    recs, probs, idx = [], [], 0
    blocks = re.split(r"\n\s*\n(?=%0|%A|%T)", text.strip())
    for b in blocks:
        f = {}
        last = None
        for line in b.splitlines():
            m = re.match(r"^%(\S)\s+(.*)$", line)
            if m:
                last = m.group(1)
                f.setdefault(last, []).append(m.group(2).strip())
            elif last and line.strip():
                f[last][-1] += " " + line.strip()
        if not f:
            continue
        idx += 1
        g = lambda k: (f.get(k) or [None])[0]
        authors = []
        for a in f.get("A", []):
            authors += split_authors(a) if re.search(r"[;；,，]", a) and has_cjk(a) else ([split_name(a)] if not re.search(r"[;；]", a) else split_authors(a))
        typ = ENW_TYPE.get((g("0") or "").lower(), ENW_TYPE.get(g("0") or "", "misc"))
        r = {"type": typ, "title": g("T"), "authors": [a for a in authors if a], "year": g("D"),
             "container": g("J") or g("B"), "volume": g("V"), "issue": g("N"), "pages": _pages(g("P")),
             "publisher": g("I"), "place": g("C"), "doi": g("R") or g("U") if norm_doi(g("R") or g("U") or "") else g("R"),
             "isbn": g("@") if typ in ("book", "chapter") else None, "url": g("U"), "abstract": g("X"),
             "keywords": [k for x in f.get("K", []) for k in re.split(r"[;；,，]", x) if k.strip()],
             "title_alt": g("Q"), "note": g("Z"),
             "src": {"file": fname, "index": idx, "format": "endnote", "raw": b[:1500]}}
        if typ == "thesis" and not r.get("publisher"):
            r["publisher"] = g("I") or g("B")
        if not r["title"]:
            probs.append({"file": fname, "index": idx, "problem": "EndNote record has no %T", "raw": b[:300]})
        recs.append(_finish(r))
    return recs, probs


# ---------------------------------------------------------------- NoteExpress (CNKI "NoteExpress" export)
def parse_noteexpress(text, fname=""):
    recs, probs, idx = [], [], 0
    for b in re.split(r"\n\s*\n", text.strip()):
        f = {}
        for line in b.splitlines():
            m = re.match(r"^\{([^}]+)\}\s*[:：]\s*(.*)$", line.strip())
            if m:
                f[m.group(1).strip().lower()] = m.group(2).strip()
        if not f:
            continue
        idx += 1
        typ = ENW_TYPE.get(f.get("reference type", "").lower(), "misc")
        r = {"type": typ, "title": f.get("title"), "authors": split_authors(f.get("author", ""), sep=r"[;；]"),
             "year": f.get("year"), "container": f.get("journal") or f.get("secondary title") or f.get("tertiary title"),
             "volume": f.get("volume"), "issue": f.get("issue"), "pages": _pages(f.get("pages")),
             "publisher": f.get("publisher"), "place": f.get("place published"), "doi": f.get("doi"),
             "isbn": f.get("isbn/issn") if typ == "book" else None, "url": f.get("url"), "abstract": f.get("abstract"),
             "keywords": [k for k in re.split(r"[;；,，]", f.get("keywords", "")) if k.strip()],
             "title_alt": f.get("translated title") or f.get("english title"),
             "src": {"file": fname, "index": idx, "format": "noteexpress", "raw": b[:1500]}}
        if not r["title"]:
            probs.append({"file": fname, "index": idx, "problem": "NoteExpress record has no {Title}", "raw": b[:300]})
        recs.append(_finish(r))
    return recs, probs


# ---------------------------------------------------------------- CSL-JSON
def parse_csl(text, fname=""):
    probs = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return [], [{"file": fname, "index": 0, "problem": f"invalid JSON: {e}", "raw": text[:200]}]
    if isinstance(data, dict):
        data = data.get("items") or data.get("references") or [data]
    recs = []
    for idx, it in enumerate(data, 1):
        if not isinstance(it, dict):
            probs.append({"file": fname, "index": idx, "problem": "item is not an object", "raw": str(it)[:200]})
            continue
        if "authors" in it and isinstance(it.get("authors"), list) and it.get("title") is not None and "author" not in it:
            r = dict(it)  # already cite-sync records
            r.setdefault("src", {"file": fname, "index": idx, "format": "cite-sync-json"})
            recs.append(_finish(r))
            continue
        y = it.get("issued", {}).get("date-parts", [[None]])[0][0] if isinstance(it.get("issued"), dict) else it.get("year")
        authors = []
        for a in it.get("author", []) or []:
            authors.append({k: v for k, v in (("family", a.get("family")), ("given", a.get("given")), ("literal", a.get("literal"))) if v})
        typ = it.get("type", "misc")
        typ = {"article": "preprint", "article-magazine": "article-journal", "article-newspaper": "article-journal",
               "post-weblog": "webpage", "post": "webpage", "manuscript": "misc"}.get(typ, typ)
        r = {"type": typ if typ in BIB_TYPE.values() or typ == "preprint" else "misc", "bibkey": it.get("id") if isinstance(it.get("id"), str) else None,
             "title": it.get("title"), "authors": authors, "year": str(y) if y else None,
             "container": it.get("container-title"), "volume": it.get("volume"), "issue": it.get("issue"),
             "pages": _pages(it.get("page")), "publisher": it.get("publisher"), "place": it.get("publisher-place"),
             "doi": it.get("DOI"), "isbn": it.get("ISBN"), "url": it.get("URL"), "abstract": it.get("abstract"),
             "keywords": [k.strip() for k in re.split(r"[;,]", it.get("keyword", "")) if k.strip()],
             "title_alt": it.get("original-title") or it.get("title-short") if it.get("original-title") else None,
             "src": {"file": fname, "index": idx, "format": "csl-json", "raw": json.dumps(it, ensure_ascii=False)[:1500]}}
        recs.append(_finish(r))
    return recs, probs


# ---------------------------------------------------------------- free-text reference strings
GBT_CODE = {"J": "article-journal", "C": "paper-conference", "M": "book", "D": "thesis", "R": "report", "S": "standard",
            "P": "patent", "N": "article-journal", "EB": "webpage", "DB": "dataset", "Z": "misc", "A": "chapter", "G": "book"}
ITEM_HEAD = re.compile(r"^\s*(?:\[(\d+)\]|［(\d+)］|(\d+)[\.\)、]|\((\d+)\))\s*")


def split_reflist(lines):
    """Join wrapped lines into entries. Returns [(label_number or None, text)]."""
    entries = []
    nonblank = [ln for ln in lines if ln.strip()]
    if nonblank and not any(ITEM_HEAD.match(ln) for ln in nonblank[:3]):
        # unnumbered list (APA / author-year): one entry per line; a line that starts with whitespace,
        # a lower-case letter or a URL continues the previous entry
        for ln in nonblank:
            st = ln.strip()
            if entries and (ln[:1].isspace() or st[:1].islower() or st.startswith("http")):
                entries[-1][1] += " " + st
            else:
                entries.append([None, re.sub(r"^\s*[-*]\s+", "", ln).strip()])
        return [(n, t) for n, t in entries if t]
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            continue
        m = ITEM_HEAD.match(s)
        if m:
            num = next(g for g in m.groups() if g)
            entries.append([int(num), s[m.end():].strip()])
        elif entries and not re.match(r"^\s*[-*]\s", s):
            entries[-1][1] += (" " if not has_cjk(s[:1]) else "") + s.strip()
        else:
            entries.append([None, re.sub(r"^\s*[-*]\s+", "", s).strip()])
    return [(n, t) for n, t in entries if t]


def parse_refstring(s, fname="", idx=0):
    """Heuristic parse of one formatted reference (GB/T 7714, APA, Vancouver/IEEE-like)."""
    s0 = s
    s = nfkc(s).strip()
    r = {"src": {"file": fname, "index": idx, "format": "reftext", "raw": s0}}
    m = re.search(r"(?:doi[:：]?\s*|https?://(?:dx\.)?doi\.org/)(10\.\d{4,9}/[^\s,;，；]+)", s, re.I)
    if m:
        r["doi"] = m.group(1).rstrip(".")
    m = re.search(r"arxiv[:\s]*(?:preprint\s*)?(?:arxiv[:\s]*)?(\d{4}\.\d{4,5}(v\d+)?)|arxiv\.org/abs/(\d{4}\.\d{4,5})", s, re.I)
    if m:
        r["arxiv"] = norm_arxiv(m.group(1) or m.group(3))
    um = re.search(r"https?://\S+", s)
    if um and "doi.org" not in um.group(0):
        r["url"] = um.group(0).rstrip(".")
    code = re.search(r"\[(J|C|M|D|R|S|P|N|EB|DB|Z|A|G)(?:/(OL|CD|MT|DK))?\]", s)
    if code:  # GB/T 7714: Authors. Title[J]. Container, Year, Vol(Issue): Pages.
        r["type"] = GBT_CODE[code.group(1)]
        head, tail = s[:code.start()], s[code.end():]
        hm = re.match(r"^(.*?)[\.．。]\s*(.+)$", head)
        if hm and len(hm.group(1)) < 400:
            auth, title = hm.group(1), hm.group(2)
            if not re.search(r"[,，、]|等|et al", auth, re.I) and len(auth.split()) > 6 and not has_cjk(auth):
                auth, title = "", head  # no author part
        else:
            auth, title = "", head
        r["title"] = title.strip()
        aus = re.sub(r"[,，]?\s*(等|et al\.?)\s*$", "", auth.strip(), flags=re.I)
        r["authors"] = [split_name(x) for x in re.split(r"[,，、]", aus) if x.strip()]
        if re.search(r"等|et al", auth, re.I):
            r["authors_truncated"] = True
        tail = tail.lstrip(". ．")
        if r["type"] == "paper-conference" or tail.startswith("//"):
            tail = tail.lstrip("/ ")
        ym = re.search(r"(?:,|，|\s)\s*((?:19|20)\d\d)[a-z]?", tail)
        if ym:
            r["year"] = ym.group(1)
            r["container"] = tail[:ym.start()].strip(" ,，.")
            rest = tail[ym.end():]
            vm = re.match(r"\s*[,，]\s*([\w\-]+)?\s*(?:\(([^)]+)\))?\s*(?::\s*([\w\-–]+))?", rest)
            if vm:
                r["volume"], r["issue"], r["pages"] = vm.group(1), vm.group(2), _pages(vm.group(3))
            if not r.get("pages"):
                pm = re.search(r":\s*(\d+[\-–]\d+|\d+)", rest)
                if pm:
                    r["pages"] = _pages(pm.group(1))
        else:
            r["container"] = tail.split(".")[0].strip()
        if r["type"] in ("book", "thesis", "report", "paper-conference"):
            pm = re.search(r"([^.,:：]+)[:：]\s*([^,，:]+)[,，]\s*((?:19|20)\d\d)", tail)
            if pm:
                r["place"], r["publisher"] = pm.group(1).strip(), pm.group(2).strip()
                if r["type"] == "paper-conference":
                    r["container"] = tail[:pm.start()].strip(" .,")
                elif r["type"] != "paper-conference":
                    r.pop("container", None)
        return _finish(r)
    am = re.match(r"^(.+?)\s*[\(（]((?:19|20)\d\d)[a-z]?[^)）]*[\)）][\.。]?\s*(.+)$", s)
    if am:  # APA: Authors (Year). Title. Container, vol(issue), pages.
        auth, r["year"], rest = am.group(1), am.group(2), am.group(3)
        names = re.split(r",\s*(?=[A-Z][^,]*,\s*[A-Z]\.)|,?\s*&\s*|;\s*", auth)
        r["authors"] = [split_name(x) for x in names if x.strip() and x.strip() not in ("...", "…")]
        tm = re.match(r"^(.+?[\.\?!])\s+(.+)$", rest)
        pm = re.match(r"^(.+?[\.\?!])\s+In\s+(.+?)\s*\(pp?\.\s*([\d\-–]+)\)\.?\s*([^.]*)\.?\s*(https?://\S+)?$", rest)
        if pm:
            r["title"] = pm.group(1).rstrip(".")
            r["container"], r["pages"], r["type"] = pm.group(2).strip(" ."), _pages(pm.group(3)), "paper-conference"
            if pm.group(4) and not pm.group(4).startswith("http"):
                r["publisher"] = pm.group(4).strip()
            return _finish(r)
        if tm:
            r["title"] = tm.group(1).rstrip(".")
            cont = tm.group(2)
            cm = re.match(r"^(?:In\s+)?(.+?)(?:,\s*(\d+)\s*(?:\(([^)]+)\))?)?(?:,\s*(?:pp?\.\s*)?(\d+[\-–]\d+|\d+))?\.?\s*(?:https?://\S+)?$", cont)
            if cm:
                r["container"], r["volume"], r["issue"], r["pages"] = cm.group(1).strip(" ."), cm.group(2), cm.group(3), _pages(cm.group(4))
            r["type"] = "article-journal" if r.get("volume") else ("paper-conference" if re.search(r"proceedings|conference|workshop", cont, re.I) else "misc")
        else:
            r["title"] = rest
        if r.get("arxiv") and (not r.get("container") or "arxiv" in r.get("container", "").lower()):
            r["type"] = "preprint"
        return _finish(r)
    # Vancouver / IEEE-ish fallback: Authors. Title. Container. Year;Vol(Issue):Pages.
    parts = [p.strip() for p in re.split(r"(?<=[^A-Z\s])\.\s+", s) if p.strip()]
    if len(parts) >= 2:
        r["authors"] = [split_name(x) for x in re.split(r",|，|\band\b", parts[0]) if x.strip()]
        r["title"] = parts[1].strip('"“”')
        if len(parts) > 2:
            r["container"] = parts[2]
    else:
        r["title"] = s
    ym = re.search(r"\b((?:19|20)\d\d)\b", s)
    if ym:
        r["year"] = ym.group(1)
    r["parse_confidence"] = "low"
    r["type"] = "preprint" if r.get("arxiv") else "misc"
    return _finish(r)


def parse_reflist_text(text, fname=""):
    recs, probs = [], []
    for idx, (num, t) in enumerate(split_reflist(text.splitlines()), 1):
        r = parse_refstring(t, fname, idx)
        if num is not None:
            r["label"] = num
        if not r.get("title"):
            probs.append({"file": fname, "index": idx, "problem": "could not find a title", "raw": t[:300]})
        recs.append(r)
    return recs, probs


def sniff(path, text):
    ext = os.path.splitext(path)[1].lower()
    t = text.lstrip()
    if ext in (".bib", ".bibtex") or re.search(r"^\s*@\w+\s*[{(]", text, re.M):
        return "bibtex"
    if ext in (".ris",) or re.search(r"^TY  - ", text, re.M):
        return "ris"
    if ext in (".enw", ".endnote") or re.search(r"^%[0AT] ", text, re.M):
        return "endnote"
    if re.search(r"^\{Reference Type\}\s*[:：]", text, re.M):
        return "noteexpress"
    if ext in (".json", ".csl") or t.startswith("[") or t.startswith("{"):
        return "csl-json"
    return "reftext"


PARSERS = {"bibtex": parse_bibtex, "ris": parse_ris, "endnote": parse_endnote, "noteexpress": parse_noteexpress,
           "csl-json": parse_csl, "reftext": parse_reflist_text}


def load_library(path):
    """-> (records, problems, format). Never raises for bad content; raises only if the file is missing."""
    text = read_text(path)
    fmt = sniff(path, text)
    fname = os.path.basename(path)
    try:
        recs, probs = PARSERS[fmt](text, fname)
    except Exception as e:  # keep going: report the file as unparseable
        return [], [{"file": fname, "index": 0, "problem": f"parser crashed ({fmt}): {e!r}", "raw": text[:200]}], fmt
    if not recs and not probs:
        probs.append({"file": fname, "index": 0, "problem": f"no records found (detected format {fmt})", "raw": text[:200]})
    return recs, probs, fmt
