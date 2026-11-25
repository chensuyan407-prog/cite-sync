"""Build the two PDF cases (python tests/make_pdf_cases.py).

tests/pdfs/ holds arXiv copies of the cited papers (not committed; downloaded here from arxiv.org when missing):
  1512.03385 ResNet, 1706.03762 Transformer, 1502.03167 BatchNorm, 2001.08361 Kaplan scaling laws.
pdf_evidence  : markdown manuscript + the 4 PDFs; one sentence cites ResNet for Kaplan's power-law finding.
pdf_manuscript: the same manuscript printed to PDF (PyMuPDF), no cited PDFs -> tests PDF -> editable conversion.
"""
import json
import os
import shutil
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PDFS = {"1512.03385": "resnet.pdf", "1706.03762": "attention.pdf", "1502.03167": "batchnorm.pdf", "2001.08361": "kaplan.pdf"}
MS = """# Notes on training and scaling deep networks

## 1 Background

Residual learning lets networks with more than 100 layers be trained and won the ILSVRC 2015 classification task [2]. Batch normalization normalizes layer inputs over each mini-batch and allows much higher learning rates [4]. The Transformer relies entirely on attention and dispenses with recurrence and convolutions [1].

## 2 Scaling

The test loss of language models scales as a power law with model size, dataset size and the amount of compute used for training [2]. Larger models are significantly more sample-efficient [3]. It has been shown that dropout reduces overfitting in large networks.

## References

[1] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems. 2017: 5998-6008.
[2] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. 2016: 770-778.
[3] Kaplan J, McCandlish S, Henighan T, et al. Scaling laws for neural language models[J]. arXiv preprint arXiv:2001.08361, 2020.
[4] Ioffe S, Szegedy C. Batch normalization: Accelerating deep network training by reducing internal covariate shift[C]//International Conference on Machine Learning. 2015: 448-456.
"""


def fetch():
    d = os.path.join(ROOT, "pdfs")
    os.makedirs(d, exist_ok=True)
    for aid, name in PDFS.items():
        p = os.path.join(d, name)
        if not os.path.exists(p):
            req = urllib.request.Request(f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": "cite-sync-tests"})
            with urllib.request.urlopen(req, timeout=60) as r, open(p, "wb") as fh:
                fh.write(r.read())
    return d


def main():
    d = fetch()
    a = os.path.join(ROOT, "cases", "pdf_evidence", "input")
    os.makedirs(a, exist_ok=True)
    open(os.path.join(a, "manuscript.md"), "w", encoding="utf-8").write(MS)
    for name in PDFS.values():
        shutil.copy(os.path.join(d, name), a)
    json.dump({"case_id": "dev-pdf-evidence", "manuscript": "manuscript.md", "sources": list(PDFS.values()),
               "output_contract": {"revised_manuscript": "edited manuscript", "references": "GB/T 7714 list", "claim_source_check": "per citation: does the cited PDF support the sentence"}},
              open(os.path.join(a, "case.json"), "w", encoding="utf-8"), ensure_ascii=False)
    b = os.path.join(ROOT, "cases", "pdf_manuscript", "input")
    os.makedirs(b, exist_ok=True)
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    y = 50
    for para in MS.split("\n"):
        text = para.lstrip("# ").strip()
        if not text:
            y += 8
            continue
        rect = fitz.Rect(50, y, 545, 800)
        h = page.insert_textbox(rect, text, fontsize=10 if not para.startswith("#") else 13, fontname="helv")
        used = (800 - y) - h if h >= 0 else 0
        y += max(14, used) + 10
        if y > 760:
            page = doc.new_page()
            y = 50
    doc.save(os.path.join(b, "manuscript_draft.pdf"))
    json.dump({"case_id": "dev-pdf-manuscript", "manuscript": "manuscript_draft.pdf", "output_contract": ["revised_manuscript", "references", "needs_review"]},
              open(os.path.join(b, "case.json"), "w", encoding="utf-8"))
    print("ok")


if __name__ == "__main__":
    main()
