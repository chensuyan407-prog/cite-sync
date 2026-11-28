"""Manuscript model: load (.md/.markdown/.txt/.tex/.docx), find the reference section, sentences and citation
markers, rewrite markers and the reference list, save in the same format.

Unit = one line (text formats) or one paragraph (docx). Sentence id = u<unit>s<k>, computed on the ORIGINAL
manuscript, so ids stay stable across re-runs with agent edits.
"""
import copy
import os
import re

from cite_common import has_cjk, nfkc, read_text

REF_HEAD = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?\s*(?:\d+[\.\s]*)?(参考文献|参考资料|引用文献|references?|bibliography|works cited|literature cited)\s*[:：]?\s*(?:\*\*)?\s*$", re.I)
END_HEAD = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?\s*(?:\d+[\.\s]*)?(附录|致谢|appendix|appendices|acknowledg(e)?ments?|supplementary|作者简介|作者贡献)", re.I)
CAPTION = re.compile(r"^\s*(?:!\[|\*{0,2}\s*(?:图|表|Fig\.?|Figure|Table|Supplementary (?:Fig|Table))\s*[S]?\d+)", re.I)
HEADING = re.compile(r"^\s*#{1,6}\s+")

NUM_BODY = r"\d+(?:\s*(?:[-–—~～]|,|，|、)\s*\d+)*"
PATTERNS = [
    ("html-sup", re.compile(r"<sup>\s*\[?(" + NUM_BODY + r")\]?\s*</sup>", re.I)),
    ("pandoc-sup", re.compile(r"\^\[(" + NUM_BODY + r")\]\^")),
    ("latex-sup", re.compile(r"\\textsuperscript\{\[?(" + NUM_BODY + r")\]?\}")),
    ("inline", re.compile(r"(?<![!A-Za-z0-9_])[\[［](" + NUM_BODY + r")[\]］](?![\(:])")),
    ("latex-cite", re.compile(r"\\(?:cite|citep|citet|parencite|textcite|autocite|supercite)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}")),
    ("pandoc-key", re.compile(r"\[(@[\w:\-\./]+(?:\s*;\s*-?@[\w:\-\./]+)*)\]")),
]
AY_PAREN = re.compile(r"[\(（]([^()（）]{2,200}?(?:19|20)\d\d[a-z]?(?:[^()（）]{0,200}?))[\)）]")
AY_ITEM = re.compile(r"^\s*(?:e\.g\.,?\s*|see\s+|参见\s*|如\s*)?([A-Z][\w'’\-]+(?:\s+(?:et al\.?|and|&)\s*(?:[A-Z][\w'’\-]+)?)?|[\u4e00-\u9fff]{1,4}(?:等|和[\u4e00-\u9fff]{1,4})?)\s*[,，]?\s*((?:19|20)\d\d)([a-z]?)\s*$")
AY_NARR = re.compile(r"([A-Z][\w'’\-]+(?:\s+(?:et al\.|and [A-Z][\w'’\-]+|& [A-Z][\w'’\-]+))?|[\u4e00-\u9fff]{1,4}等?)\s*[\(（]((?:19|20)\d\d)([a-z]?)[\)）]")
ABBR = re.compile(r"(?:\bet al|\be\.g|\bi\.e|\bFig|\bFigs|\bEq|\bEqs|\bvs|\bNo|\bRef|\bRefs|\bSec|\bcf|\bapprox|\bDr|\bProf|\bVol|\bpp|\bp|\bal|\b[A-Z])\.$")


def parse_nums(s):
    s = nfkc(s).replace("～", "~").replace("—", "-").replace("–", "-")
    out = []
    for part in re.split(r"[,，、]", s):
        part = part.strip()
        m = re.match(r"^(\d+)\s*[-~]\s*(\d+)$", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b and b - a < 200:
                out += list(range(a, b + 1))
            else:
                out += [a, b]
        elif part.isdigit():
            out.append(int(part))
    return out


# ---------------------------------------------------------------- loading
def _docx_units(path):
    import docx
    from docx.oxml.ns import qn
    d = docx.Document(path)
    units = []
    body = d.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            els = [child]
        elif child.tag == qn("w:tbl"):
            els = list(child.iter(qn("w:p")))
        else:
            continue
        for p in els:
            runs = [r for r in p.iterchildren() if r.tag == qn("w:r")]
            text, runmap, sup = "", [], []
            for ri, r in enumerate(runs):
                t = "".join((x.text or "") if x.tag == qn("w:t") else ("\t" if x.tag == qn("w:tab") else "") for x in r.iterchildren())
                va = r.find(qn("w:rPr") + "/" + qn("w:vertAlign"))
                is_sup = va is not None and va.get(qn("w:val")) == "superscript"
                text += t
                runmap += [ri] * len(t)
                sup += [is_sup] * len(t)
            style = p.find(qn("w:pPr") + "/" + qn("w:pStyle"))
            sname = style.get(qn("w:val")) if style is not None else ""
            fields = bool(list(p.iter(qn("w:fldChar")))) or bool(list(p.iter(qn("w:fldSimple"))))
            hidden = bool(list(p.iter(qn("w:hyperlink"))))
            units.append({"text": text, "runmap": runmap, "sup": sup, "el": p, "style": sname,
                          "has_fields": fields, "has_hyperlink": hidden, "in_table": child.tag == qn("w:tbl")})
    return d, units


def load(path):
    ext = os.path.splitext(path)[1].lower()
    doc = {"path": path, "kind": {".md": "md", ".markdown": "md", ".txt": "txt", ".tex": "tex", ".docx": "docx"}.get(ext)}
    if doc["kind"] is None:
        raise ValueError(f"unsupported manuscript format {ext!r}: use .md/.txt/.tex/.docx (convert .doc/.pdf/.odt first)")
    if doc["kind"] == "docx":
        doc["docx"], doc["units"] = _docx_units(path)
    else:
        raw = read_text(path)
        doc["newline"] = "\r\n" if "\r\n" in raw else "\n"
        doc["units"] = [{"text": t} for t in raw.replace("\r\n", "\n").split("\n")]
    _roles(doc)
    return doc


def _is_heading(doc, u):
    if doc["kind"] == "docx":
        st = (u.get("style") or "").lower()
        return st.startswith("heading") or st.startswith("title") or bool(re.match(r"^\d+$", st))
    return bool(HEADING.match(u["text"])) or (doc["kind"] == "tex" and bool(re.match(r"\s*\\(sub)*section\*?\{", u["text"])))


def _roles(doc):
    units = doc["units"]
    ref_start = ref_end = None
    for i, u in enumerate(units):
        t = u["text"].strip()
        if REF_HEAD.match(t) or (doc["kind"] == "tex" and re.match(r"\\begin\{thebibliography\}", t)):
            ref_start = i  # last matching heading wins (a heading 'References' inside the text is rare)
    if ref_start is not None:
        ref_end = len(units)
        for j in range(ref_start + 1, len(units)):
            t = units[j]["text"].strip()
            if END_HEAD.match(t) or (_is_heading(doc, units[j]) and t and not re.match(r"^\s*(\[\d+\]|\d+[\.\)])", t)) \
                    or (doc["kind"] == "tex" and t.startswith("\\end{thebibliography}")):
                ref_end = j
                break
    doc["ref_start"], doc["ref_end"] = ref_start, ref_end
    for i, u in enumerate(units):
        t = u["text"]
        if ref_start is not None and i == ref_start:
            u["role"] = "ref_heading"
        elif ref_start is not None and ref_start < i < ref_end:
            u["role"] = "reflist"
        elif _is_heading(doc, u):
            u["role"] = "heading"
        elif CAPTION.match(t) or (doc["kind"] == "docx" and "caption" in (u.get("style") or "").lower()):
            u["role"] = "caption"
        elif ref_end is not None and i >= ref_end:
            u["role"] = "appendix"
        else:
            u["role"] = "body"


def reflist_lines(doc):
    if doc["ref_start"] is None:
        return []
    return [(i, doc["units"][i]["text"]) for i in range(doc["ref_start"] + 1, doc["ref_end"])]


# ---------------------------------------------------------------- markers + sentences
def find_markers(u):
    """-> list of {start, end, style, kind: num|key|ay|ay-narr, nums|keys|ay, raw}"""
    t = u["text"]
    taken = [False] * len(t)
    out = []

    def add(s, e, **kw):
        if any(taken[s:e]):
            return
        for k in range(s, e):
            taken[k] = True
        out.append(dict(start=s, end=e, raw=t[s:e], **kw))

    for style, rx in PATTERNS:
        for m in rx.finditer(t):
            if style in ("latex-cite", "pandoc-key"):
                keys = [k.strip().lstrip("-@") for k in re.split(r"[,;]", m.group(1)) if k.strip()]
                add(m.start(), m.end(), style=style, kind="key", keys=keys)
            else:
                nums = parse_nums(m.group(1))
                if nums and max(nums) < 2000:
                    add(m.start(), m.end(), style=style, kind="num", nums=nums)
    if u.get("sup"):
        i = 0
        while i < len(t):
            if u["sup"][i] and not taken[i]:
                j = i
                while j < len(t) and u["sup"][j]:
                    j += 1
                seg = t[i:j]
                m = re.fullmatch(r"\s*[\[［]?(" + NUM_BODY + r")[\]］]?\s*", seg)
                if m:
                    add(i, j, style="docx-sup", kind="num", nums=parse_nums(m.group(1)))
                i = j
            else:
                i += 1
    for m in re.finditer(r"[\[［]([^\[\]]+)[\]］]", t):  # bracket groups with the docx superscript already handled
        pass
    for m in AY_PAREN.finditer(t):
        items = []
        for part in re.split(r"[;；]", m.group(1)):
            im = AY_ITEM.match(part.strip())
            if not im:
                items = []
                break
            items.append({"name": im.group(1), "year": im.group(2), "suffix": im.group(3)})
        if items:
            add(m.start(), m.end(), style="ay-paren", kind="ay", ay=items)
    for m in AY_NARR.finditer(t):
        add(m.start(), m.end(), style="ay-narr", kind="ay", ay=[{"name": m.group(1), "year": m.group(2), "suffix": m.group(3)}], narrative=True)
    if u.get("sup"):  # docx: a bracketed marker typed in superscript runs is a superscript marker
        for mk in out:
            if mk["kind"] == "num" and mk["style"] == "inline" and all(u["sup"][k] for k in range(mk["start"], mk["end"]) if not t[k].isspace()):
                mk["style"] = "docx-sup"
    out.sort(key=lambda x: x["start"])
    # glue adjacent numeric markers: [1][2] / [1], [2] / [1]-[3] -> one occurrence
    merged = []
    for mk in out:
        if merged and mk["kind"] == "num" and merged[-1]["kind"] == "num" and mk["style"] == merged[-1]["style"]:
            gap = t[merged[-1]["end"]:mk["start"]]
            if re.fullmatch(r"\s*[,，、]?\s*", gap) or re.fullmatch(r"\s*[-–~～]\s*", gap):
                p = merged[-1]
                if re.fullmatch(r"\s*[-–~～]\s*", gap) and len(p["nums"]) == 1 and len(mk["nums"]) == 1:
                    p["nums"] = list(range(p["nums"][0], mk["nums"][0] + 1))
                else:
                    p["nums"] = p["nums"] + mk["nums"]
                p["end"] = mk["end"]
                p["raw"] = t[p["start"]:p["end"]]
                p["glued"] = True
                continue
        merged.append(mk)
    return merged


TERM = "。！？!?；;"


def sentences(text, markers):
    """Split into sentence spans [(s, e)]; markers are masked so their dots/brackets do not split."""
    masked = list(text)
    for mk in markers:
        for k in range(mk["start"], mk["end"]):
            masked[k] = "\x00"
    m = "".join(masked)
    spans, s = [], 0
    i = 0
    while i < len(m):
        c = m[i]
        cut = None
        if c in "。！？!?" and not (c == "!" and m[i + 1:i + 2] == "["):
            cut = i + 1
        elif c == "." and (i + 1 == len(m) or m[i + 1] in " \t\x00\"”'’)"):
            if not ABBR.search(m[max(0, i - 8):i + 1]) and not re.match(r"\d", m[i + 1:i + 2] or "x"):
                cut = i + 1
        if cut:
            k = cut
            while k < len(m) and m[k] in "\"”'’)）":
                k += 1
            # a marker right after the terminal punctuation belongs to this sentence
            while k < len(m) and m[k] in " \x00":
                if m[k] == "\x00":
                    while k < len(m) and m[k] == "\x00":
                        k += 1
                else:
                    j = k
                    while j < len(m) and m[j] == " ":
                        j += 1
                    if j < len(m) and m[j] == "\x00":
                        k = j
                    else:
                        break
            if m[s:k].strip():
                spans.append((s, k))
            s = k
            i = k
            continue
        i += 1
    if m[s:].strip():
        spans.append((s, len(m)))
    return spans


def analyse(doc):
    """Attach markers and sentences to every non-reflist unit. -> (occurrences, sentences)"""
    occs, sents = [], []
    for ui, u in enumerate(doc["units"]):
        if u["role"] in ("reflist", "ref_heading"):
            u["markers"], u["sents"] = [], []
            continue
        mk = find_markers(u)
        if u["role"] == "heading":
            mk = [m for m in mk if m["kind"] != "ay"]
        sp = sentences(u["text"], mk)
        u["markers"] = mk
        u["sents"] = []
        for k, (s, e) in enumerate(sp):
            sid = f"u{ui}s{k}"
            u["sents"].append({"id": sid, "start": s, "end": e})
            sents.append({"id": sid, "unit": ui, "start": s, "end": e, "role": u["role"], "text": u["text"][s:e].strip(),
                          "is_last_in_unit": k == len(sp) - 1, "n_in_unit": len(sp)})
        for j, m in enumerate(mk):
            sid = next((x["id"] for x in u["sents"] if x["start"] <= m["start"] < x["end"]), u["sents"][-1]["id"] if u["sents"] else f"u{ui}s0")
            m.update(id=f"c{ui}_{j}", unit=ui, sentence=sid, role=u["role"])
            occs.append(m)
    return occs, sents


def plain(text, markers=()):
    """Sentence text without citation markers (for matching)."""
    out, last = [], 0
    for m in sorted(markers, key=lambda x: x["start"]):
        out.append(text[last:m["start"]])
        last = m["end"]
    out.append(text[last:])
    return re.sub(r"\s+", " ", "".join(out)).strip()


# ---------------------------------------------------------------- rewriting
def insertion_point(text, s, e):
    """Inside sentence [s,e): position before the terminal punctuation (and trailing markers/quotes)."""
    k = e
    while k > s and text[k - 1] in " \t":
        k -= 1
    while k > s and text[k - 1] in "\"”'’)）":
        k -= 1
    if k > s and text[k - 1] in TERM + ".，,：:":
        k -= 1
    while k > s and text[k - 1] == " ":
        k -= 1
    return k


def build_unit(u, ops):
    """ops: list of (start, end, newtext, sup) replacements on the original text (start==end: insertion).
    -> pieces [(char, src_index|None, sup|None)]"""
    t = u["text"]
    ops = sorted(ops, key=lambda o: (o[0], o[1]))
    pieces, pos = [], 0
    for s, e, new, sup in ops:
        if s < pos:
            continue
        pieces += [(t[k], k, None) for k in range(pos, s)]
        pieces += [(ch, None, sup) for ch in new]
        pos = e
    pieces += [(t[k], k, None) for k in range(pos, len(t))]
    return pieces


def tidy(pieces, marker_chars=None):
    """Remove doubled spaces left by deleted markers ('word  .' -> 'word.')."""
    out = []
    for i, p in enumerate(pieces):
        if p[0] == " " and out and out[-1][0] == " ":
            continue
        if p[0] in ".,;:。，；：)" and out and out[-1][0] == " " and out[-1][1] is not None and (len(out) < 2 or out[-2][0] not in "])"):
            out.pop()
        out.append(p)
    return out


def save(doc, new_units, path, reflist=None, ref_prefix="[{n}] "):
    """new_units: {unit_index: pieces}; reflist: list of rendered entries (str) or None to keep."""
    if doc["kind"] == "docx":
        return _save_docx(doc, new_units, path, reflist)
    lines = []
    for i, u in enumerate(doc["units"]):
        if reflist is not None and doc["ref_start"] is not None and doc["ref_start"] < i < doc["ref_end"]:
            if i == doc["ref_start"] + 1:
                if not u["text"].strip():
                    lines.append("")
                if doc["kind"] == "tex":
                    lines += [f"\\bibitem{{{k}}} {txt}" for k, txt in reflist]
                else:
                    for n, txt in enumerate(reflist, 1):
                        lines.append(ref_prefix.format(n=n) + txt)
                        if doc.get("ref_blank_lines"):
                            lines.append("")
                    if doc["ref_end"] < len(doc["units"]):
                        lines.append("")
            continue
        if i in new_units:
            lines.append("".join(p[0] for p in new_units[i]))
        else:
            lines.append(u["text"])
    if reflist is not None and doc["ref_start"] is None and doc["kind"] != "tex":
        lines += ["", "## 参考文献" if doc.get("zh") else "## References", ""] + [ref_prefix.format(n=n) + t for n, t in enumerate(reflist, 1)]
    with open(path, "w", encoding="utf-8", newline=doc.get("newline", "\n")) as fh:
        fh.write("\n".join(lines))
    return []


def _save_docx(doc, new_units, path, reflist):
    from docx.oxml.ns import qn
    warnings = []
    for i, pieces in new_units.items():
        u = doc["units"][i]
        p = u["el"]
        runs = [r for r in p.iterchildren() if r.tag == qn("w:r")]
        if not runs:
            continue
        if u.get("has_fields"):
            warnings.append(f"unit {i}: paragraph contains Word field codes (EndNote/Zotero/cross-reference); rewritten as plain text")
        # assign a source run to every char
        groups, prev_run = [], 0
        for ch, src, sup in pieces:
            if src is not None:
                ri = u["runmap"][src] if src < len(u["runmap"]) else prev_run
                s = u["sup"][src] if sup is None else sup
            else:
                ri, s = prev_run, bool(sup)
            prev_run = ri
            if groups and groups[-1][0] == ri and groups[-1][1] == s:
                groups[-1][2].append(ch)
            else:
                groups.append([ri, s, [ch]])
        anchor = runs[0]
        new_els = []
        for ri, s, chars in groups:
            el = copy.deepcopy(runs[min(ri, len(runs) - 1)])
            for x in list(el):
                if x.tag != qn("w:rPr"):
                    el.remove(x)
            rpr = el.find(qn("w:rPr"))
            if rpr is None:
                rpr = el.makeelement(qn("w:rPr"), {})
                el.insert(0, rpr)
            va = rpr.find(qn("w:vertAlign"))
            if s:
                if va is None:
                    va = rpr.makeelement(qn("w:vertAlign"), {})
                    rpr.append(va)
                va.set(qn("w:val"), "superscript")
            elif va is not None and va.get(qn("w:val")) == "superscript":
                rpr.remove(va)
            tt = el.makeelement(qn("w:t"), {})
            tt.text = "".join(chars)
            tt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            el.append(tt)
            new_els.append(el)
        for el in new_els:
            anchor.addprevious(el)
        for r in runs:
            p.remove(r)
    if reflist is not None and doc["ref_start"] is not None:
        olds = [doc["units"][i]["el"] for i in range(doc["ref_start"] + 1, doc["ref_end"])]
        tmpl = olds[0] if olds else doc["units"][doc["ref_start"]]["el"]
        head = doc["units"][doc["ref_start"]]["el"]
        last = head
        for n, txt in enumerate(reflist, 1):
            np_ = copy.deepcopy(tmpl)
            runs = [r for r in np_.iterchildren() if r.tag == qn("w:r")]
            for r in runs[1:]:
                np_.remove(r)
            if runs:
                r = runs[0]
                for x in list(r):
                    if x.tag != qn("w:rPr"):
                        r.remove(x)
                rpr = r.find(qn("w:rPr"))
                if rpr is not None and rpr.find(qn("w:vertAlign")) is not None:
                    rpr.remove(rpr.find(qn("w:vertAlign")))
            else:
                r = np_.makeelement(qn("w:r"), {})
                np_.append(r)
            tt = r.makeelement(qn("w:t"), {})
            tt.text = doc.get("ref_prefix", "[{n}] ").format(n=n) + txt
            tt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            r.append(tt)
            last.addnext(np_)
            last = np_
        for el in olds:
            el.getparent().remove(el)
    for line in doc.get("appendix_lines") or []:
        doc["docx"].add_paragraph(line)
    doc["docx"].save(path)
    return warnings
