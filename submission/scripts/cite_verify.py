"""Source checks and claim-citation support hints.

Offline checks (always): required fields for the target style, DOI syntax, DOI prefix vs venue, arXiv id vs year,
page range, ISBN checksum, year range, truncated author lists.
Online checks (--online, best effort, cached, time-boxed): Crossref /works/{doi}, Crossref title search when the
DOI is missing, arXiv API for preprints, published-version lookup for preprints. Network failure -> every record
keeps status 'unverified_offline'; nothing is invented.

Support hints: lexical overlap between the citing sentence and the record's title / alt title / abstract /
keywords, with a small zh<->en term lexicon and method-name aliases. The score is a HINT for the agent, who
writes the final verdict per citation occurrence.
"""
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from cite_common import (author_overlap, has_cjk, is_preprint, nfkc, norm_doi, sim, surname, title_key, tokens, year_of)

UA = "cite-sync/0.1 (citation checking skill; mailto:cite-sync@users.noreply.github.com)"

VENUE_PREFIX = [
    (r"^nature\b|nature (communications|methods|physics|genetics|medicine|biotechnology|machine intelligence)", ["10.1038"]),
    (r"^science$|science (advances|robotics|translational)", ["10.1126"]),
    (r"\bieee\b|cvpr|iccv|transactions on (pattern|image|neural|signal|information)", ["10.1109"]),
    (r"\bacm\b|communications of the acm|siggraph|\bkdd\b|\bchi\b", ["10.1145"]),
    (r"neural computation", ["10.1162"]),
    (r"\b(acl|naacl|emnlp|eacl|coling)\b|association for computational linguistics", ["10.18653"]),
    (r"proceedings of the national academy|^pnas", ["10.1073"]),
    (r"physical review", ["10.1103"]),
    (r"^cell$|the lancet|^lancet|neuron$|pattern recognition$|neural networks$|neurocomputing", ["10.1016"]),
    (r"plos", ["10.1371"]),
    (r"lecture notes|\beccv\b|springer", ["10.1007"]),
    (r"arxiv", ["10.48550"]),
    (r"biorxiv|medrxiv", ["10.1101"]),
]
PREFIX_NAME = {"10.1038": "Springer Nature (Nature)", "10.1126": "AAAS (Science)", "10.1109": "IEEE", "10.1145": "ACM",
               "10.1162": "MIT Press", "10.18653": "ACL Anthology", "10.1073": "PNAS", "10.1103": "APS", "10.1016": "Elsevier",
               "10.1371": "PLOS", "10.1007": "Springer", "10.48550": "arXiv", "10.1101": "Cold Spring Harbor (bioRxiv)",
               "10.1002": "Wiley", "10.1093": "Oxford UP", "10.1017": "Cambridge UP", "10.3390": "MDPI", "10.12677": "Hans Publishers"}
REQUIRED = {"gbt7714": {"article-journal": ["authors", "title", "container", "year", "pages"],
                        "paper-conference": ["authors", "title", "container", "year"],
                        "book": ["authors", "title", "publisher", "year"], "thesis": ["authors", "title", "publisher", "year"],
                        "report": ["authors", "title", "year"], "preprint": ["authors", "title", "year"],
                        "webpage": ["title", "url"], "chapter": ["authors", "title", "container", "publisher", "year"]},
            "apa7": {"article-journal": ["authors", "title", "container", "year", "volume"],
                     "paper-conference": ["authors", "title", "container", "year"], "book": ["authors", "title", "publisher", "year"],
                     "preprint": ["authors", "title", "year"], "webpage": ["title", "url"]}}


def isbn_ok(s):
    d = re.sub(r"[^0-9Xx]", "", s or "")
    if len(d) == 13:
        return sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(d)) % 10 == 0
    if len(d) == 10:
        return sum((10 - i) * (10 if c in "Xx" else int(c)) for i, c in enumerate(d)) % 11 == 0
    return False


def offline_checks(r, style="gbt7714"):
    issues = []
    req = REQUIRED.get(style, REQUIRED["gbt7714"]).get(r.get("type"), ["authors", "title", "year"])
    for f in req:
        if not r.get(f):
            issues.append({"code": "missing_field", "field": f, "severity": "warn", "msg": f"{f} missing for {r.get('type')}"})
    if r.get("type") == "article-journal" and not (r.get("volume") or r.get("issue")):
        issues.append({"code": "missing_field", "field": "volume/issue", "severity": "warn", "msg": "journal article without volume/issue"})
    raw_doi = (r.get("src") or {}).get("raw", "")
    if r.get("doi_raw_invalid"):
        issues.append({"code": "bad_doi", "severity": "error", "msg": f"DOI not parseable: {r['doi_raw_invalid']}"})
    d = r.get("doi")
    c = (r.get("container") or "").lower()
    if d and c:
        pre = d.split("/")[0]
        for rx, exp in VENUE_PREFIX:
            if re.search(rx, c):
                if pre not in exp and not (pre == "10.1162" and "computational linguistics" in c):
                    issues.append({"code": "doi_venue_mismatch", "severity": "error",
                                   "msg": f"venue '{r.get('container')}' normally has DOI prefix {exp[0]} ({PREFIX_NAME.get(exp[0], '')}), record has {pre} ({PREFIX_NAME.get(pre, 'unknown registrant')})"})
                break
    y = year_of(r)
    now = dt.date.today().year
    if r.get("year") and (y is None or y < 1600 or y > now + 1):
        issues.append({"code": "bad_year", "severity": "error", "msg": f"implausible year {r.get('year')}"})
    if r.get("arxiv") and y and re.match(r"\d{4}\.", r["arxiv"]):
        ay = 2000 + int(r["arxiv"][:2])
        if is_preprint(r) and abs(ay - y) > 1:
            issues.append({"code": "arxiv_year_mismatch", "severity": "warn", "msg": f"arXiv id {r['arxiv']} was submitted in {ay}, record year {y}"})
        if not is_preprint(r) and y < ay:
            issues.append({"code": "arxiv_year_mismatch", "severity": "warn", "msg": f"published year {y} is before arXiv submission {ay}"})
    p = r.get("pages") or ""
    m = re.match(r"^(\d+)\s*[-–]\s*(\d+)$", p)
    if m and int(m.group(2)) < int(m.group(1)):
        issues.append({"code": "bad_pages", "severity": "error", "msg": f"page range {p} decreases"})
    if r.get("isbn") and not isbn_ok(r["isbn"]):
        issues.append({"code": "bad_isbn", "severity": "warn", "msg": f"ISBN checksum fails: {r['isbn']}"})
    if r.get("authors_truncated"):
        issues.append({"code": "authors_truncated", "severity": "info", "msg": "source list was truncated ('et al./等'); full author list not available offline"})
    if r.get("parse_confidence") == "low":
        issues.append({"code": "low_parse_confidence", "severity": "warn", "msg": "free-text reference could not be parsed reliably"})
    return issues


# ---------------------------------------------------------------- online
class Net:
    def __init__(self, cache_path, enabled=True, budget_s=20, max_requests=40, timeout=4):
        self.cache_path = cache_path
        self.cache = {}
        if cache_path and os.path.exists(cache_path):
            try:
                self.cache = json.load(open(cache_path, encoding="utf-8"))
            except Exception:
                self.cache = {}
        self.enabled, self.budget, self.maxr, self.timeout = enabled, budget_s, max_requests, timeout
        self.t0, self.n, self.offline_reason = time.time(), 0, None if enabled else "online checks not requested"
        self.errors = []

    def get(self, url, kind="json"):
        if url in self.cache:
            return self.cache[url]
        if not self.enabled or self.offline_reason:
            return None
        if time.time() - self.t0 > self.budget or self.n >= self.maxr:
            self.offline_reason = f"network budget used ({self.n} requests, {round(time.time() - self.t0)} s)"
            return None
        for attempt in range(2):
            self.n += 1
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8", "replace")
                val = {"status": 200, "body": json.loads(body) if kind == "json" else body}
            except urllib.error.HTTPError as e:
                val = {"status": e.code, "body": None}
                if e.code == 429 or e.code >= 500:  # rate limit / server error: wait, retry once, never cache
                    self.errors.append(f"{url}: HTTP {e.code}")
                    if attempt == 0:
                        time.sleep(3)
                        continue
                    return val
            except Exception as e:  # DNS / timeout / no network: stop trying
                self.errors.append(f"{url}: {e!r}")
                self.net_fail = getattr(self, "net_fail", 0) + 1
                if self.net_fail >= 1:  # first DNS/timeout/connection failure: go offline at once
                    self.offline_reason = f"network unavailable ({e!r})"
                return None
            self.cache[url] = val
            return val

    def save(self):
        if self.cache_path:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            json.dump(self.cache, open(self.cache_path, "w", encoding="utf-8"), ensure_ascii=False)


def _cr_to_rec(m):
    y = None
    for k in ("published-print", "published-online", "issued", "published"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            y = dp[0][0]
            break
    ct = m.get("container-title") or []
    typ = {"journal-article": "article-journal", "proceedings-article": "paper-conference", "book-chapter": "chapter",
           "book": "book", "posted-content": "preprint", "monograph": "book", "dissertation": "thesis", "report": "report"}.get(m.get("type"), "misc")
    return {"doi": norm_doi(m.get("DOI")), "title": (m.get("title") or [""])[0], "year": str(y) if y else None,
            "container": ct[-1] if ct else None, "volume": m.get("volume"), "issue": m.get("issue"), "pages": (m.get("page") or "").replace("--", "-") or None,
            "publisher": m.get("publisher"), "type": typ,
            "authors": [{"family": a.get("family"), "given": a.get("given")} if a.get("family") else {"literal": a.get("name", "")} for a in m.get("author", [])]}


def crossref_doi(net, doi):
    v = net.get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    if v is None:
        return None, "no_response"
    if v["status"] == 404:
        return None, "not_found"
    if v["status"] != 200:
        return None, f"http_{v['status']}"
    return _cr_to_rec(v["body"]["message"]), "ok"


def crossref_search(net, r, rows=5):
    q = (r.get("title") or "") + " " + " ".join((a.get("family") or a.get("literal") or "") for a in (r.get("authors") or [])[:2])
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": q.strip(), "rows": rows,
                                                                       "select": "DOI,title,container-title,volume,issue,page,issued,published-print,published-online,author,type,publisher"})
    v = net.get(url)
    if not v or v["status"] != 200:
        return None
    return [_cr_to_rec(m) for m in v["body"]["message"].get("items", [])]


def arxiv_lookup(net, aid):
    v = net.get("http://export.arxiv.org/api/query?id_list=" + aid, kind="text")
    if not v or v["status"] != 200 or "<entry>" not in (v["body"] or ""):
        return None
    e = v["body"].split("<entry>", 1)[1]
    t = re.search(r"<title>(.*?)</title>", e, re.S)
    pub = re.search(r"<published>(\d{4})", e)
    names = re.findall(r"<name>(.*?)</name>", e)
    if not t or "Error" in t.group(1):
        return None
    from cite_common import split_name
    return {"title": re.sub(r"\s+", " ", t.group(1)).strip(), "year": pub.group(1) if pub else None,
            "authors": [split_name(n) for n in names]}


COMPARE = ["year", "container", "volume", "issue", "pages"]


def online_check(net, r, apply=True):
    """-> (status, details, corrections{field: (old, new, source)})"""
    det, corr = {}, {}
    if not net.enabled:
        return "unverified_offline", {"reason": net.offline_reason}, corr
    reg = None
    if r.get("doi") and not r["doi"].startswith("10.48550/"):
        reg, st = crossref_doi(net, r["doi"])
        det["crossref_doi"] = st
        if st == "no_response":
            return "unverified_offline", {"reason": net.offline_reason or "no response"}, corr
        if st == "not_found":
            det["doi_not_found"] = r["doi"]
    if reg is None and r.get("arxiv") and is_preprint(r):
        ax = arxiv_lookup(net, r["arxiv"])
        if ax:
            ts = sim(ax["title"], r.get("title"))
            det["arxiv"] = {"title": ax["title"], "year": ax["year"], "title_similarity": round(ts, 3)}
            if ts < 0.85:
                return "mismatch", dict(det, problem="arXiv id resolves to a different title"), corr
            hits = crossref_search(net, r) or []
            pub = [h for h in hits if h["type"] != "preprint" and sim(h["title"], r.get("title")) >= 0.95 and not (h.get("doi") or "").startswith("10.48550")]
            if pub:
                det["published_version"] = {k: pub[0].get(k) for k in ("doi", "container", "year", "pages")}
            for f in ("year",):
                if not r.get(f) and ax.get(f):
                    corr[f] = (None, ax[f], f"arXiv:{r['arxiv']}")
            return "verified", det, corr
        det["arxiv"] = "no response or id not found"
    if reg is None:
        hits = crossref_search(net, r)
        if hits is None:
            return ("doi_not_found" if det.get("doi_not_found") else "unverified_offline"), dict(det, reason=net.offline_reason or "search failed"), corr
        def ok(h):
            ov_ = author_overlap(h.get("authors"), r.get("authors"))
            yh, yr = year_of(h), year_of(r)
            # a title hit alone is not enough: Crossref holds copies/translations/junk records with famous titles
            return (sim(h["title"], r.get("title")) >= 0.9 and ov_ is not None and ov_ >= 0.5
                    and (yh is None or yr is None or abs(yh - yr) <= 1))
        good = [h for h in hits if ok(h)]
        best = max(good or hits, key=lambda h: sim(h["title"], r.get("title")), default=None)
        bs = sim(best["title"], r.get("title")) if best else 0
        ov = author_overlap(best.get("authors"), r.get("authors")) if best else None
        det["search_best"] = {"doi": best.get("doi") if best else None, "title": best.get("title") if best else None, "year": best.get("year") if best else None,
                              "similarity": round(bs, 3), "author_overlap": ov, "accepted": bool(good)}
        if not good:
            if r.get("arxiv"):
                ax = arxiv_lookup(net, r["arxiv"])
                if ax and sim(ax["title"], r.get("title")) >= 0.85:
                    det["arxiv"] = {"title": ax["title"], "year": ax["year"], "note": "work confirmed via its arXiv record; venue metadata not in Crossref"}
                    return "verified_via_arxiv", det, corr
            if det.get("doi_not_found"):
                return "doi_not_found", det, corr
            c = (r.get("container") or "").lower()
            doi_venue = any(re.search(rx, c) for rx, exp in VENUE_PREFIX if exp[0] not in ("10.48550", "10.1101"))
            if r.get("type") == "article-journal" and not is_preprint(r) and doi_venue:
                # journals of these publishers register every article: absence is a strong fabrication signal
                return "not_found", dict(det, note=f"'{r.get('container')}' registers DOIs for all articles"), corr
            # many venues never register DOIs (JMLR, PMLR, ICLR, older NeurIPS, many Chinese journals)
            return "unverified_no_registry_match", det, corr
        best = max(good, key=lambda h: sim(h["title"], r.get("title")))
        reg = best
        if det.get("doi_not_found"):
            corr["doi"] = (r.get("doi"), reg["doi"], "crossref title search (recorded DOI does not resolve)")
        elif not r.get("doi"):
            corr["doi"] = (None, reg["doi"], "crossref title search")
    ts = sim(reg["title"], r.get("title")) if r.get("title") else 1.0
    alt = sim(reg["title"], r.get("title_alt")) if r.get("title_alt") else 0
    det["registry"] = {k: reg.get(k) for k in ("doi", "title", "year", "container", "volume", "issue", "pages")}
    det["title_similarity"] = round(max(ts, alt), 3)
    if max(ts, alt) < 0.8:
        return "mismatch", dict(det, problem="DOI resolves to a different work (title differs)"), corr
    fa = surname((r.get("authors") or [None])[0]), surname((reg.get("authors") or [None])[0])
    if fa[0] and fa[1] and fa[0] != fa[1] and not has_cjk(r.get("title")):
        det["first_author_mismatch"] = {"record": fa[0], "registry": fa[1]}
    nr, ng = len(r.get("authors") or []), len(reg.get("authors") or [])
    if ng and nr and ng < nr:
        det["registry_author_list_shorter"] = f"registry lists {ng} author(s), record has {nr}; kept the record's list"
    if ng > nr and nr and fa[0] and fa[0] == fa[1] and not has_cjk(r.get("title")):
        corr["authors"] = (f"{nr} author(s)", reg["authors"], f"crossref (registry lists {ng} authors; record had {nr})")
    for f in COMPARE:
        a, b = r.get(f), reg.get(f)
        if not b:
            continue
        if f == "container":
            if not a:
                corr[f] = (a, b, "crossref")
            elif sim(a, b) < 0.5 and title_key(a) not in title_key(b) and title_key(b) not in title_key(a):
                det.setdefault("container_differs", []).append({"record": a, "registry": b})
            continue
        if f == "year" and a and b and abs(int(str(a)[:4]) - int(str(b)[:4])) == 1 and r.get("type") == "paper-conference":
            continue  # proceedings dated in the following year
        na, nb = (str(a).replace("–", "-").strip() if a else ""), str(b).replace("–", "-").strip()
        if f == "volume":
            na, nb = na.lstrip("0"), nb.lstrip("0")
        if f == "issue":
            na, nb = na.lstrip("0"), nb.lstrip("0")
        if na != nb:
            corr[f] = (a, b, "crossref")
    if det.get("first_author_mismatch"):
        return "mismatch", dict(det, problem="first author differs from registry"), corr
    return ("verified_with_corrections" if corr else "verified"), det, corr


# ---------------------------------------------------------------- claim-citation support hints
LEX = {"深度学习": "deep learning", "残差": "residual", "注意力": "attention", "卷积": "convolutional", "池化": "pooling",
       "批归一化": "batch normalization", "批量归一化": "batch normalization", "归一化": "normalization", "预训练": "pre-training",
       "长短期记忆": "long short-term memory", "蛋白质": "protein", "结构预测": "structure prediction", "图像识别": "image recognition",
       "图像分类": "image classification", "分类": "classification", "语言模型": "language models", "规模": "scaling",
       "缩放": "scaling", "优化": "optimization", "随机": "stochastic", "神经网络": "neural networks", "识别": "recognition",
       "双向": "bidirectional", "变换器": "transformer", "语言理解": "language understanding", "实例分割": "instance segmentation",
       "目标检测": "object detection", "恒等映射": "identity mappings", "梯度": "gradient", "循环": "recurrent",
       "过拟合": "overfitting", "丢弃": "dropout", "机器翻译": "translation", "综述": "survey", "特征": "feature",
       "强化学习": "reinforcement learning", "生成": "generative", "对抗": "adversarial", "扩散": "diffusion",
       "知识图谱": "knowledge graph", "推荐": "recommendation", "检索": "retrieval", "大模型": "large language models",
       "大语言模型": "large language models", "微调": "fine-tuning", "迁移学习": "transfer learning", "自监督": "self-supervised",
       "训练": "training", "残差学习": "residual learning", "深层": "deep", "上百层": "deep layers", "层": "layers",
       "注意力机制": "attention mechanism", "掩码": "masked", "少样本": "few-shot", "图卷积": "graph convolutional",
       "半监督": "semi-supervised", "节点": "node", "图结构": "graph", "损失": "loss", "幂律": "power law", "模型规模": "model size",
       "测试": "test", "卷积神经网络": "convolutional neural networks", "循环神经网络": "recurrent neural networks", "加速": "accelerating", "协变量偏移": "covariate shift", "精度": "accurate", "准确": "accurate",
       "算力": "compute", "参数": "parameters", "数据集": "dataset", "表示": "representations"}
ALIASES = {"resnet": "deep residual learning", "transformer": "attention is all you need", "alexnet": "imagenet classification",
           "lstm": "long short-term memory", "bn": "batch normalization", "batchnorm": "batch normalization", "adam": "adam stochastic optimization",
           "dropout": "dropout", "bert": "bert", "alphafold": "alphafold protein structure", "mask r-cnn": "mask r-cnn",
           "gpt-3": "language models are few-shot learners", "vit": "an image is worth 16x16 words"}
STOP = set("the a an of for and in on to with by from via is are be as at its this that we our using based".split())


def record_text(r):
    return " ".join(str(x) for x in [r.get("title"), r.get("title_alt"), r.get("abstract"), " ".join(r.get("keywords") or [])] if x)


def expand(sentence):
    s = nfkc(sentence)
    extra = [en for zh, en in LEX.items() if zh in s]
    low = s.lower()
    extra += [v for k, v in ALIASES.items() if re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", low)]
    return s + " " + " ".join(extra)


def support(sentence, r):
    """-> (score 0..1, matched terms). Overlap of record title/abstract terms found in the sentence."""
    st = {t for t in tokens(expand(sentence)) if t not in STOP and len(t) > 1}
    rt = [t for t in tokens(record_text(r)) if t not in STOP and len(t) > 1]
    tt = [t for t in tokens((r.get("title") or "") + " " + (r.get("title_alt") or "")) if t not in STOP and len(t) > 1]
    if not tt:
        return 0.0, []
    stem = lambda w: re.sub(r"(ing|ions?|al|s|es|ed)$", "", w) if re.match(r"[a-z]", w) else w
    ss = {stem(t) for t in st}
    hit_t = sorted({t for t in tt if stem(t) in ss})
    hit_r = sorted({t for t in rt if stem(t) in ss})
    score = 0.7 * len(hit_t) / len(set(tt)) + 0.3 * min(1.0, len(hit_r) / 6)
    fam = [surname(a) for a in (r.get("authors") or [])[:1] if surname(a)]
    if fam and re.search(r"(?<![a-z])" + re.escape(fam[0]) + r"(?![a-z])", title_key(sentence) and sentence.lower()):
        score += 0.2
        hit_t.append("author:" + fam[0])
    return round(min(1.0, score), 3), hit_t


CLAIM_CUES = re.compile(r"研究表明|研究发现|已有研究|有研究|已被证明|被证明|被广泛|广泛(应用|使用|采用)|普遍认为|据报道|有学者|学者们|先前|此前|最先进|首次|提出了|取得了|显著(提升|提高|优于)|"
                        r"has been shown|have shown|studies (show|have)|prior work|previous(ly)? (work|stud)|widely (used|adopted)|state[- ]of[- ]the[- ]art|"
                        r"it is (well )?known|was (first )?(proposed|introduced)|were (proposed|introduced)|reported|outperform|achiev(e|ed|es) .*\d", re.I)
OWN = re.compile(r"本文|我们|本研究|本工作|\b(we|our|this (paper|work|study))\b", re.I)


def claim_cue(sentence):
    if OWN.search(sentence) and not re.search(r"(?:如|正如|following|as in|like)\s", sentence):
        return None
    m = CLAIM_CUES.search(sentence)
    if m:
        return m.group(0)
    if re.search(r"\d+(\.\d+)?\s*(%|×|倍|percent)", sentence):
        return "number"
    return None
