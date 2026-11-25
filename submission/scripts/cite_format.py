"""Renderers: GB/T 7714-2015 (numeric), APA 7th, BibTeX, RIS, CSL-JSON; in-text marker rendering.

Each render_* returns (text, missing_fields). missing_fields lists what the target style needs but the
record lacks; the caller turns them into review items instead of inventing values.
"""
import json
import re

from cite_common import has_cjk, initials, title_key

GBT_CODE = {"article-journal": "J", "paper-conference": "C", "book": "M", "chapter": "M", "thesis": "D", "report": "R",
            "standard": "S", "patent": "P", "webpage": "EB/OL", "dataset": "DB/OL", "preprint": "EB/OL", "misc": "Z"}


def _gbt_name(a, upper=False):
    if a.get("literal"):
        return a["literal"]
    fam, giv = a.get("family", ""), a.get("given", "")
    if has_cjk(fam):
        return fam + giv
    fam = fam.upper() if upper else fam
    ini = initials(giv)
    return f"{fam} {ini}".strip()


def gbt_authors(r, upper=False, max_n=3):
    au = [a for a in r.get("authors") or [] if a.get("literal") != "et al."]
    zh = r.get("lang") == "zh" or has_cjk(r.get("title"))
    etal = "等" if zh else "et al"
    trunc = r.get("authors_truncated") or any(a.get("literal") == "et al." for a in r.get("authors") or [])
    if not au:
        return ""
    names = [_gbt_name(a, upper) for a in au]
    if len(names) > max_n or (trunc and len(names) <= max_n):
        return ", ".join(names[:max_n]) + ", " + etal
    return ", ".join(names)


def render_gbt(r, opts=None):
    o = opts or {}
    t = r.get("type", "misc")
    code = GBT_CODE.get(t, "Z")
    miss = []
    au = gbt_authors(r, o.get("upper"))
    title = r.get("title") or ""
    if not title:
        miss.append("title")
    year = r.get("year") or ""
    if not year:
        miss.append("year")
    head = (au + ". " if au else "") + title
    pages = (r.get("pages") or "").replace("–", "-")
    if t == "article-journal":
        if not r.get("container"):
            miss.append("container")
        s = f"{head}[J]. {r.get('container', '')}, {year}"
        if r.get("volume"):
            s += f", {r['volume']}"
        if r.get("issue"):
            s += f"({r['issue']})"
        if not (r.get("volume") or r.get("issue")):
            miss.append("volume/issue")
        if pages:
            s += f": {pages}"
        else:
            miss.append("pages")
    elif t == "paper-conference":
        if not r.get("container"):
            miss.append("container")
        s = f"{head}[C]//{r.get('container', '')}"
        if r.get("place") and r.get("publisher"):
            s += f". {r['place']}: {r['publisher']}, {year}"
        elif r.get("publisher"):
            s += f". {r['publisher']}, {year}"
        else:
            s += f", {year}"
        if pages:
            s += f": {pages}"
    elif t in ("book", "chapter", "thesis", "report", "standard"):
        s = f"{head}[{code}]"
        if t == "chapter" and r.get("container"):
            s += f"//{r['container']}"
        if r.get("edition") and str(r.get("edition")) not in ("1", "1st"):
            ed = str(r["edition"])
            s += f". {ed}" + ("版" if has_cjk(title) and ed.isdigit() else (" ed" if ed.isdigit() else ""))
        if r.get("place") or r.get("publisher"):
            s += f". {r.get('place') or '[出版地不详]' if has_cjk(title) else r.get('place') or '[S.l.]'}: {r.get('publisher') or ('[出版者不详]' if has_cjk(title) else '[s.n.]')}, {year}"
            if not r.get("place"):
                miss.append("place")
            if not r.get("publisher"):
                miss.append("publisher")
        else:
            miss += ["place", "publisher"]
            s += f". {year}"
        if pages and t in ("chapter",):
            s += f": {pages}"
    elif t in ("preprint", "webpage", "dataset"):
        url = r.get("url") or (f"https://arxiv.org/abs/{r['arxiv']}" if r.get("arxiv") else "")
        if t == "preprint" and r.get("arxiv") and not o.get("preprint_eb"):
            # common Chinese-journal practice for arXiv preprints, keeps the identifier visible
            s = f"{head}[J/OL]. arXiv preprint arXiv:{r['arxiv']}, {year}"
            if url:
                s += f". {url}"
        else:
            s = f"{head}[{code}]."
            if r.get("publisher") or r.get("container"):
                s += f" {r.get('publisher') or r.get('container')},"
            s += f" ({year})"
            if r.get("accessed"):
                s += f"[{r['accessed']}]"
            else:
                miss.append("accessed (引用日期)")
            if url:
                s += f". {url}"
            else:
                miss.append("url")
    else:
        s = f"{head}[Z]. " + ", ".join(x for x in (r.get("container"), r.get("publisher"), year) if x)
    s = s.rstrip(". ")
    if r.get("doi") and not s.lower().endswith(r["doi"].lower()):
        s += f". DOI:{r['doi']}"
    return s + ".", miss


def _apa_name(a):
    if a.get("literal"):
        return a["literal"]
    fam, giv = a.get("family", ""), a.get("given", "")
    if has_cjk(fam):
        return fam + giv
    ini = initials(giv, dots=True)
    return f"{fam}, {ini}" if ini else fam


def apa_authors(r):
    au = [a for a in r.get("authors") or [] if a.get("literal") != "et al."]
    names = [_apa_name(a) for a in au]
    if not names:
        return ""
    if has_cjk(r.get("title")):
        return "，".join(names)
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:19]) + ", ... " + names[-1]


def render_apa(r, opts=None):
    t = r.get("type", "misc")
    miss = []
    au = apa_authors(r) or (r.get("title") or "")
    year = f"({r.get('year') or 'n.d.'}{r.get('year_suffix', '')})"
    if not r.get("year"):
        miss.append("year")
    title = r.get("title") or ""
    pages = (r.get("pages") or "").replace("-", "–")
    if t == "article-journal":
        s = f"{au} {year}. {title}. {r.get('container', '')}"
        if not r.get("container"):
            miss.append("container")
        if r.get("volume"):
            s += f", {r['volume']}"
            if r.get("issue"):
                s += f"({r['issue']})"
        if pages:
            s += f", {pages}"
        s += "."
    elif t == "paper-conference":
        s = f"{au} {year}. {title}. In {r.get('container', '')}" + (f" (pp. {pages})" if pages else "") + "."
        if r.get("publisher"):
            s += f" {r['publisher']}."
    elif t in ("book", "report", "thesis"):
        s = f"{au} {year}. {title}" + (f" ({r['edition']} ed.)" if r.get("edition") and str(r['edition']) not in ("1",) else "") + "."
        if r.get("publisher"):
            s += f" {r['publisher']}."
        else:
            miss.append("publisher")
    elif t == "preprint":
        repo = "arXiv" if (r.get("arxiv") or "arxiv" in (r.get("container") or "").lower()) else (r.get("container") or r.get("publisher") or "")
        s = f"{au} {year}. {title}" + (f" (arXiv:{r['arxiv']})" if r.get("arxiv") else "") + (f". {repo}." if repo else ".")
        if not r.get("doi") and r.get("arxiv"):
            s += f" https://doi.org/10.48550/arXiv.{r['arxiv']}"
    else:
        s = f"{au} {year}. {title}." + (f" {r['container']}." if r.get("container") else "")
    if r.get("doi"):
        s += f" https://doi.org/{r['doi']}"
    elif r.get("url"):
        s += f" {r['url']}"

    return re.sub(r"\s+", " ", s).replace("..", ".").strip(), miss


BIB_OUT = {"article-journal": "article", "paper-conference": "inproceedings", "book": "book", "chapter": "incollection",
           "thesis": "phdthesis", "report": "techreport", "preprint": "misc", "webpage": "online", "misc": "misc",
           "standard": "misc", "patent": "misc", "dataset": "misc"}


def bibkey(r, used):
    if r.get("bibkey") and r["bibkey"] not in used:
        used.add(r["bibkey"])
        return r["bibkey"]
    a = (r.get("authors") or [{}])[0]
    fam = a.get("family") or a.get("literal") or "anon"
    base = re.sub(r"[^A-Za-z0-9]", "", fam.lower()) or ("ref" + title_key(fam)[:4])
    w = re.findall(r"[A-Za-z]{4,}", r.get("title") or "")
    base = f"{base}{r.get('year', '')}{(w[0].lower() if w else '')}"
    k, i = base, 1
    while k in used:
        i += 1
        k = f"{base}{chr(96 + i)}"
    used.add(k)
    return k


def _bib_esc(s):
    return str(s).replace("&", "\\&").replace("%", "\\%")


def render_bibtex(recs):
    used, out = set(), []
    for r in recs:
        k = bibkey(r, used)
        t = BIB_OUT.get(r.get("type"), "misc")
        f = []
        au = " and ".join((f"{a['family']}, {a.get('given', '')}".strip(", ") if a.get("family") else "{" + a.get("literal", "") + "}")
                          for a in r.get("authors") or [] if a.get("literal") != "et al.")
        if r.get("authors_truncated") or any(a.get("literal") == "et al." for a in r.get("authors") or []):
            au += " and others"
        f.append(("author", au))
        f.append(("title", "{" + _bib_esc(r.get("title", "")) + "}"))
        ck = {"article": "journal", "inproceedings": "booktitle", "incollection": "booktitle"}.get(t)
        if ck and r.get("container"):
            f.append((ck, _bib_esc(r["container"])))
        for a, b in (("year", "year"), ("volume", "volume"), ("issue", "number"), ("pages", "pages"),
                     ("publisher", "publisher" if t not in ("phdthesis", "techreport") else ("school" if t == "phdthesis" else "institution")),
                     ("place", "address"), ("edition", "edition"), ("doi", "doi"), ("isbn", "isbn"), ("url", "url"), ("accessed", "urldate")):
            if r.get(a):
                v = str(r[a]).replace("–", "--").replace("-", "--") if a == "pages" else r[a]
                f.append((b, _bib_esc(v) if a not in ("url", "doi") else v))
        if r.get("arxiv"):
            f += [("eprint", r["arxiv"]), ("archiveprefix", "arXiv")]
        if r.get("title_alt"):
            f.append(("title_alt", r["title_alt"]))
        out.append(f"@{t}{{{k},\n" + ",\n".join(f"  {a} = {{{b}}}" if not b.startswith("{") else f"  {a} = {b}" for a, b in f if b) + "\n}")
    return "\n\n".join(out) + "\n"


RIS_OUT = {"article-journal": "JOUR", "paper-conference": "CPAPER", "book": "BOOK", "chapter": "CHAP", "thesis": "THES",
           "report": "RPRT", "preprint": "UNPB", "webpage": "ELEC", "standard": "STAND", "patent": "PAT", "dataset": "DATA", "misc": "GEN"}


def render_ris(recs):
    out = []
    for r in recs:
        L = [f"TY  - {RIS_OUT.get(r.get('type'), 'GEN')}"]
        for a in r.get("authors") or []:
            if a.get("literal") == "et al.":
                continue
            L.append("AU  - " + (f"{a['family']}, {a.get('given', '')}".strip(", ") if a.get("family") else a.get("literal", "")))
        L.append(f"TI  - {r.get('title', '')}")
        if r.get("title_alt"):
            L.append(f"TT  - {r['title_alt']}")
        if r.get("container"):
            L.append(f"T2  - {r['container']}")
        for k, tag in (("year", "PY"), ("volume", "VL"), ("issue", "IS"), ("publisher", "PB"), ("place", "CY"), ("doi", "DO"),
                       ("isbn", "SN"), ("url", "UR")):
            if r.get(k):
                L.append(f"{tag}  - {r[k]}")
        if r.get("pages"):
            p = re.split(r"[-–]", r["pages"])
            L.append(f"SP  - {p[0]}")
            if len(p) > 1:
                L.append(f"EP  - {p[1]}")
        if r.get("arxiv"):
            L.append(f"N1  - arXiv:{r['arxiv']}")
        L.append("ER  - ")
        out.append("\n".join(L))
    return "\n\n".join(out) + "\n"


def render_csl(recs):
    items = []
    for r in recs:
        it = {"id": r.get("bibkey") or r["id"], "type": {"preprint": "article", "misc": "document"}.get(r.get("type"), r.get("type")),
              "title": r.get("title"), "author": [{k: v for k, v in a.items() if k in ("family", "given", "literal")} for a in r.get("authors") or []],
              "container-title": r.get("container"), "volume": r.get("volume"), "issue": r.get("issue"), "page": r.get("pages"),
              "publisher": r.get("publisher"), "publisher-place": r.get("place"), "DOI": r.get("doi"), "ISBN": r.get("isbn"),
              "URL": r.get("url") or (f"https://arxiv.org/abs/{r['arxiv']}" if r.get("arxiv") else None)}
        if r.get("year"):
            it["issued"] = {"date-parts": [[int(r["year"])]]}
        items.append({k: v for k, v in it.items() if v not in (None, "", [])})
    return json.dumps(items, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- in-text markers
def compress(nums, range_sep="-", list_sep=","):
    """[1,2,3,5] -> '1-3,5'; two consecutive numbers stay as a list (1,2)."""
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            out.append(f"{nums[i]}{range_sep}{nums[j]}")
        else:
            out += [str(n) for n in nums[i:j + 1]]
        i = j + 1
    return list_sep.join(out)


def numeric_marker(nums, style="inline", range_sep="-", list_sep=","):
    body = "[" + compress(nums, range_sep, list_sep) + "]"
    if style == "unicode-sup":
        return compress(nums, "⁻", ",").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return {"inline": body, "pandoc-sup": f"^{body}^", "html-sup": f"<sup>{body}</sup>",
            "latex-sup": f"\\textsuperscript{{{body}}}", "docx-sup": body}.get(style, body)


def author_year_label(r, zh_text=False):
    au = [a for a in r.get("authors") or [] if a.get("literal") != "et al."]
    zh = has_cjk(r.get("title"))
    fam = lambda a: a.get("family") or a.get("literal") or "?"
    if not au:
        name = (r.get("title") or "?")[:20]
    elif len(au) == 1 and not r.get("authors_truncated"):
        name = fam(au[0])
    elif len(au) == 2 and not r.get("authors_truncated"):
        name = f"{fam(au[0])}{'和' if zh else ' & '}{fam(au[1])}"
    else:
        name = f"{fam(au[0])}{'等' if zh else ' et al.'}"
    return f"{name}, {r.get('year') or 'n.d.'}{r.get('year_suffix', '')}"


def author_year_marker(recs, zh_text=False):
    labels = sorted(author_year_label(r) for r in recs)
    return ("（" + "；".join(labels) + "）") if zh_text else ("(" + "; ".join(labels) + ")")
