"""Shared helpers for cite-sync: record model, text normalisation, similarity, JSON IO.

A record is a plain dict. Keys (all optional except id):
  id, type, title, title_alt, authors[{family, given, literal}], year, container, volume, issue,
  pages, publisher, place, edition, doi, arxiv, isbn, url, accessed, lang, abstract, keywords[],
  bibkey, note, src{file, index, format, raw}
type is one of: article-journal, paper-conference, book, chapter, thesis, report, preprint,
  webpage, standard, patent, dataset, misc
"""
import difflib
import hashlib
import json
import os
import re
import unicodedata

TYPES = ["article-journal", "paper-conference", "book", "chapter", "thesis", "report", "preprint",
         "webpage", "standard", "patent", "dataset", "misc"]

CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def has_cjk(s):
    return bool(s and CJK.search(s))


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c))


def title_key(s):
    """Comparable form of a title: NFKC, no accents, lower case, letters/digits/CJK only."""
    s = strip_accents(nfkc(s)).lower()
    s = re.sub(r"\\[a-z]+\s*", "", s)  # latex commands
    return "".join(c for c in s if c.isalnum())


def tokens(s):
    """Word tokens for latin text plus CJK character bigrams."""
    s = strip_accents(nfkc(s)).lower()
    out = re.findall(r"[a-z][a-z0-9\-]+|\d+(?:\.\d+)?", s)
    cj = "".join(CJK.findall(s))
    for part in re.findall(r"[\u3400-\u9fff\uf900-\ufaff]+", s):
        out += [part[i:i + 2] for i in range(len(part) - 1)] or [part]
    return out


def sim(a, b):
    """Title similarity in [0,1] on normalised keys."""
    ka, kb = title_key(a), title_key(b)
    if not ka or not kb:
        return 0.0
    if ka == kb:
        return 1.0
    return difflib.SequenceMatcher(None, ka, kb).ratio()


def norm_doi(d):
    if not d:
        return ""
    d = nfkc(d).strip()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d, flags=re.I)
    d = re.sub(r"^doi:\s*", "", d, flags=re.I)
    d = d.strip().rstrip(".,;")
    return d if re.match(r"^10\.\d{4,9}/\S+$", d) else ""


def norm_arxiv(a):
    if not a:
        return ""
    a = nfkc(a).strip()
    a = re.sub(r"^(arxiv[:\s]*|https?://arxiv\.org/(abs|pdf)/)", "", a, flags=re.I)
    m = re.match(r"(\d{4}\.\d{4,5})(v\d+)?", a) or re.match(r"([a-z\-]+(\.[A-Z]{2})?/\d{7})(v\d+)?", a)
    return m.group(1) if m else ""


ARXIV_DOI = re.compile(r"^10\.48550/arxiv\.(.+)$", re.I)


def surname(a):
    """Normalised family name of an author dict (or literal)."""
    if not a:
        return ""
    f = a.get("family") or a.get("literal") or ""
    if has_cjk(f) and not a.get("family"):
        f = f[:1]  # Chinese literal name: surname = first char (two-char surnames are rare; flagged by caller)
    return title_key(f)


def author_overlap(A, B):
    sa = {surname(x) for x in A or [] if surname(x)}
    sb = {surname(x) for x in B or [] if surname(x)}
    if not sa or not sb:
        return None
    return len(sa & sb) / min(len(sa), len(sb))


def year_of(r):
    try:
        return int(str(r.get("year", ""))[:4])
    except ValueError:
        return None


def is_preprint(r):
    c = (r.get("container") or "").lower()
    return (r.get("type") == "preprint" or "arxiv" in c or "biorxiv" in c or "medrxiv" in c or "preprint" in c
            or bool(ARXIV_DOI.match(r.get("doi") or "")) or (bool(r.get("arxiv")) and not r.get("container")))


def split_name(s):
    """'He, Kaiming' / 'Kaiming He' / 'He K' / '何恺明' -> author dict."""
    s = nfkc(s).strip().strip(",;")
    s = re.sub(r"\s+", " ", s)
    if not s:
        return None
    if has_cjk(s):
        return {"literal": s.replace(" ", "")}
    if s.lower() in ("others", "et al", "et al.", "等"):
        return {"literal": "et al."}
    if "," in s:
        fam, giv = s.split(",", 1)
        return {"family": fam.strip(), "given": giv.strip()}
    parts = s.split(" ")
    if len(parts) == 1:
        return {"family": parts[0], "given": ""}
    # 'He K' or 'He K M' or 'LeCun Y'  (GB/T / Vancouver: family first, initials after)
    if all(re.fullmatch(r"[A-Z]\.?(-[A-Z]\.?)?", p) for p in parts[1:]):
        return {"family": parts[0], "given": " ".join(parts[1:])}
    # particles: van, de, von ...
    i = len(parts) - 1
    while i > 1 and parts[i - 1].lower() in ("van", "von", "de", "der", "da", "di", "le", "la", "del", "dos"):
        i -= 1
    return {"family": " ".join(parts[i:]), "given": " ".join(parts[:i])}


def initials(given, dots=False, space=" "):
    """'Kaiming' -> 'K'; 'Diederik P.' -> 'D P'; 'Ming-Wei' -> 'M W' (GB/T) ; dots=True -> 'D. P.'"""
    out = []
    for p in re.split(r"[\s\.]+", given or ""):
        if not p:
            continue
        for q in p.split("-"):
            if q:
                out.append(q[0].upper() + ("." if dots else ""))
    return space.join(out)


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "gb18030", "utf-16"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def dump(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def first_author_label(r):
    a = (r.get("authors") or [{}])[0]
    return a.get("family") or a.get("literal") or "?"


def short(r):
    return f"{first_author_label(r)} {r.get('year', '?')} {(r.get('title') or '')[:60]}"
