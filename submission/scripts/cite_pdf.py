"""PDF helpers: text per page (PyMuPDF, else `pdftotext`), match a PDF to a reference record, find the passage of a
cited PDF that best supports a citing sentence, and turn a PDF manuscript into an editable markdown file.

Nothing is invented: a PDF that cannot be read is reported with the reason; a record without a matched PDF keeps
metadata-only support.
"""
import os
import re
import shutil
import subprocess

from cite_common import has_cjk, nfkc, norm_doi, title_key, tokens


def pdf_pages(path):
    """-> (pages[str], error|None)"""
    try:
        import fitz  # PyMuPDF
        d = fitz.open(path)
        if d.needs_pass:
            return [], "encrypted PDF (password required)"
        pages = [p.get_text("text") for p in d]
        return pages, None if any(p.strip() for p in pages) else "no text layer (scanned PDF: OCR needed)"
    except ImportError:
        pass
    except Exception as e:
        return [], f"PyMuPDF could not open the file: {e!r}"
    exe = shutil.which("pdftotext")
    if not exe:
        return [], "no PDF text tool (install PyMuPDF or poppler pdftotext)"
    try:
        out = subprocess.run([exe, "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
    except Exception as e:
        return [], f"pdftotext failed: {e!r}"
    pages = out.split("\f")
    return pages, None if any(p.strip() for p in pages) else "no text layer (scanned PDF: OCR needed)"


def match_pdf(pages, records):
    """-> (record id, basis) for the record this PDF is (DOI on page 1-2, else title on page 1, else arXiv id)."""
    head = nfkc(" ".join(pages[:2]))
    dois = {norm_doi(m.group(1)).lower() for m in re.finditer(r"(10\.\d{4,9}/[^\s\"<>,;]+)", head)}
    for r in records:
        if r.get("doi") and r["doi"].lower() in dois:
            return r["id"], f"DOI {r['doi']} printed on page 1-2"
    k1 = title_key(" ".join(pages[:1]))[:6000]
    best, bl = None, 0
    for r in records:
        tk = title_key(r.get("title"))
        if len(tk) >= 12 and tk in k1 and len(tk) > bl:
            best, bl = r, len(tk)
        ta = title_key(r.get("title_alt"))
        if len(ta) >= 8 and ta in k1 and len(ta) > bl:
            best, bl = r, len(ta)
    if best:
        return best["id"], "title printed on page 1"
    for r in records:
        if r.get("arxiv") and r["arxiv"] in head:
            return r["id"], f"arXiv id {r['arxiv']} printed on page 1-2"
    return None, None


def _sentences(page_text):
    t = re.sub(r"-\n(?=[a-z])", "", page_text)
    t = re.sub(r"\s*\n\s*", " ", t)
    parts = re.split(r"(?<=[。！？!?])|(?<=[a-z0-9\)][\.\?!])\s+(?=[A-Z\(\[])", t)
    return [p.strip() for p in parts if p and len(p.strip()) > 20]


def best_passage(pages, sentence_expanded, max_pages=40):
    """-> {page, quote, score, terms} of the 1-2 sentence window sharing most terms with the citing sentence."""
    from cite_verify import STOP
    q = {x for x in tokens(sentence_expanded) if len(x) > 2 and x not in STOP and x not in GENERIC}
    if not q:
        return None
    best = None
    for pi, pg in enumerate(pages[:max_pages]):
        ss = _sentences(pg)
        for i in range(len(ss)):
            win = ss[i] + (" " + ss[i + 1] if i + 1 < len(ss) and len(ss[i]) < 160 else "")
            wt = set(tokens(win))
            hit = q & wt
            sc = len(hit) / len(q)
            if not best or sc > best["score"]:
                best = {"page": pi + 1, "quote": win[:400], "score": round(sc, 3), "terms": sorted(hit)[:12]}
    return best


GENERIC = set("than more much most also used using use which their there these those such been have has was were can may into over each other between both all any some only very well".split())
HEAD_RX = re.compile(r"^(\d+(\.\d+)*\.?\s+\S.{0,60}|[一二三四五六七八九十]+[、.．]\s*\S.{0,40}|abstract|摘要|introduction|引言|conclusions?|结论|致谢|acknowledg(e)?ments?|appendix|附录)$", re.I)


def _blocks(path):
    try:
        import fitz
        d = fitz.open(path)
        return [[b[4] for b in sorted(p.get_text("blocks"), key=lambda b: (round(b[1]), b[0])) if b[6] == 0] for p in d]
    except Exception:
        pages, _ = pdf_pages(path)
        return [re.split(r"\n\s*\n", pg) for pg in pages]


def pdf_to_markdown(path, out_md):
    """Editable markdown from a PDF manuscript: one paragraph per text block; short numbered lines become headings;
    a 参考文献/References line starts the list; a list printed as one block is split at [n]."""
    pages, err = pdf_pages(path)
    if err:
        return None, err
    lines = []
    for blocks in _blocks(path):
        for b in blocks:
            s = re.sub(r"-\n(?=[a-z])", "", b.strip())
            s = re.sub(r"\s*\n\s*", "" if has_cjk(s) else " ", s)
            if not s or re.fullmatch(r"\d{1,4}", s):  # page numbers
                continue
            if re.fullmatch(r"(参考文献|references|bibliography)", s.strip().lower()):
                s = "## " + s
            elif HEAD_RX.match(s.strip()) and not re.search(r"[。.!?；;]$", s.strip()):
                s = "## " + s
            # a reference list printed as one block: split at [n]
            if re.match(r"^\[\d+\]", s) and len(re.findall(r"\[\d+\]", s)) > 1:
                lines += [x.strip() for x in re.split(r"(?=\[\d+\]\s)", s) if x.strip()]
            else:
                lines.append(s)
            lines.append("")
    with open(out_md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    return out_md, None


def index_pdfs(paths, records):
    """-> ({record_id: {path, pages, basis}}, problems[])"""
    found, probs = {}, []
    for p in paths:
        pages, err = pdf_pages(p)
        if err:
            probs.append({"file": os.path.basename(p), "index": 0, "problem": f"PDF not usable: {err}"})
            continue
        rid, basis = match_pdf(pages, records)
        if not rid:
            probs.append({"file": os.path.basename(p), "index": 0, "problem": "PDF does not match any reference record (no DOI/title/arXiv id on page 1-2)"})
            continue
        found.setdefault(rid, {"path": p, "pages": pages, "basis": basis})
    return found, probs
