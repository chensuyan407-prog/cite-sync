"""Build tests/cases/zh_docx/input/manuscript.docx from the dev markdown manuscript:
superscript citation runs, a bold phrase, a heading style, a caption paragraph and a reference list."""
import os, re, sys, shutil, json
import docx
from docx.shared import Pt
ROOT = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(ROOT, "cases", "zh_review", "input")
dst = os.path.join(ROOT, "cases", "zh_docx", "input")
os.makedirs(dst, exist_ok=True)
lines = open(os.path.join(src, "manuscript.md"), encoding="utf-8").read().splitlines()
d = docx.Document()
for ln in lines:
    if not ln.strip():
        continue
    if ln.startswith("#"):
        lvl = len(ln) - len(ln.lstrip("#"))
        d.add_heading(ln.lstrip("# ").strip(), level=min(lvl, 3))
        continue
    if ln.startswith("!["):
        p = d.add_paragraph(style="Caption")
        ln = re.sub(r"^!\[(.*)\]\(.*\)$", r"\1", ln)
    else:
        p = d.add_paragraph()
    ln = ln.replace("<sup>", "").replace("</sup>", "")
    is_ref = bool(re.match(r"^\[\d+\]\s", ln))
    pos = 0
    for m in ([] if is_ref else list(re.finditer(r"\[[\d,\-–]+\](?:\[[\d,\-–]+\])*", ln))):
        seg = ln[pos:m.start()]
        if "深度学习" in seg:  # one bold phrase to check that formatting survives
            a, b = seg.split("深度学习", 1)
            p.add_run(a); r = p.add_run("深度学习"); r.bold = True; p.add_run(b)
        else:
            p.add_run(seg)
        r = p.add_run(m.group(0)); r.font.superscript = True
        pos = m.end()
    p.add_run(ln[pos:])
d.save(os.path.join(dst, "manuscript.docx"))
for f in ("library.bib", "zotero.ris", "cnki.enw"):
    shutil.copy(os.path.join(src, f), dst)
json.dump({"case_id": "dev-zh-docx", "manuscript": "manuscript.docx", "output_contract": {"revised_manuscript": "", "references": "", "needs_review": ""}},
          open(os.path.join(dst, "case.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok", dst)
