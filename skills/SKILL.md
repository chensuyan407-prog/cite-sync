---
name: cite-sync
description: 参考文献与引用管理 / citation & reference-list management. Use for any task on a manuscript (.md/.txt/.docx/.tex, also .pdf/.doc which are converted) and/or reference libraries (BibTeX, RIS, EndNote/CNKI .enw, NoteExpress, CSL-JSON, numbered text lists) that asks to insert or place citations, renumber [n] after insert/delete/reorder, sync text numbers with the reference list, de-duplicate entries (zh/en titles, preprint vs published, different database exports), convert to GB/T 7714-2015 / APA 7 / BibTeX / RIS, or verify that references exist and that each cited sentence matches its source (Crossref/arXiv, and the cited papers' PDFs when supplied). One command does the bookkeeping and writes a complete result.json with every output_contract field filled, a per-citation verdict with its basis, the merge rule per duplicate, every change, and what still needs a human; you then judge only the doubtful items.
---

# cite-sync v0.2.0

脚本负责记账（编号、文献表同步、去重、格式、注册库/PDF 核验）；你负责判断（这句话是否真的需要、真的对得上这条文献）。
`SKILL_DIR` = 本文件所在目录（`/skills/weekly-skill`）。Python ≥3.9；.docx 需 python-docx；PDF 需 PyMuPDF 或 pdftotext（镜像已有）。

## 预算（64 次请求 / 900 秒）——按这个顺序做，第 1 步之后就已有完整可交付结果

1. **一条命令跑完全部**（约 5–60 s；在线核验有 120 s 上限，无网络会自动转离线）：
   ```bash
   PY=$(command -v python3 || command -v python)
   for d in "${SKILL_DIR:-}" /skills/weekly-skill /app/submission /app/skills "$(pwd)"; do
     [ -f "$d/scripts/cite.py" ] && SKILL_DIR="$d" && break
   done
   "$PY" "$SKILL_DIR/scripts/cite.py" auto --case /input/case.json --out /app/output --work /app/work
   ```
   它会：找出稿件 / 文献库 / PDF / task.md → 去重 → 核验 → 重排编号、同步文献表 → 写出可编辑稿件和
   `/app/output/result.json`（含全部 output_contract 字段与 case_id）→ 写 `/app/work/brief.md`。
   自动选错文件时用 `--manuscript F --library L1 --library L2 --pdf P --style gbt7714|apa7` 覆盖；无网络加 `--offline`。
2. **读 `/app/work/brief.md`**（短，只列需要你判断的事）和 `/input/task.md`。核对：目标规范、稿件是否选对、
   契约字段是否都已填（brief 第 5 节列出没能自动映射的字段）。
3. **只判断 brief 里列出的项**，写 `/app/work/edits.json`（结构见 `/app/work/edits_template.json`）：
   - 第 1 节（阻断项/数据冲突）：缺失文献、DOI 不可解析/疑似编造、去重冲突、元数据冲突、疑似错引（另一篇 PDF 更匹配）。
   - 第 2 节（启发式未能确认的引用）：给 `verdict` 与 `note`，必要时 `action`。
   - 第 3 节（缺引用的论断）：脚本已给出候选文献和可直接粘贴的 `add_citations` 条目；**只在你确认该文献确实支持该句时采用**。
   其余引用已有 `verdict_source: heuristic` 的 supported（依据写在 `match_basis`），可保留；读过来源的再改为你的判断。
4. **带 edits 再跑一次同一命令**：`... auto --case /input/case.json --out /app/output --work /app/work --edits /app/work/edits.json`。
   编号从头重算，写出的文件被重新解析校验（`consistency_check`），result.json 重写。
5. **收尾**：打开 result.json 看 `status`、`status_reason`、`consistency_check.ok`、`contract_unfilled`。
   契约里脚本没映射到的字段由你按 task.md 填写真实内容（不要编造）。仍有人工确认项时保持 `status: partial` 并写明原因。

若时间/请求快用完：第 1 步的输出已经是合法、诚实的部分结果——不要为“完整”而编造判断。

## edits.json

```json
{"occurrences": {
   "c4_2":  {"verdict": "supported", "note": "ResNet 论文给出 152 层网络在 ImageNet 上的结果"},
   "c20_1": {"action": "remove", "verdict": "unverifiable", "note": "DOI 无法解析，Crossref 无匹配，疑似编造"},
   "c8_0":  {"action": "replace", "refs": ["M3"], "verdict": "supported", "note": "该句是 Kaplan 2020 的结论，原引 ResNet 为错引"},
   "c9_1":  {"move_to": "text:长短期记忆网络通过门控", "move_refs": ["M4"], "verdict": "supported"}},
 "add_citations": [{"sentence": "text:语言模型的测试损失随模型参数量", "refs": ["L2-2"], "verdict": "supported", "note": "Kaplan 2020"}],
 "record_overrides": {"M5": {"pages": "84-90", "_source": "期刊官网/原文 PDF 第 1 页"}},
 "force_merge": [["M3", "L2-4"]], "forbid_merge": [["M1", "M2"]]}
```
- verdict: `supported` | `partial` | `mismatch` | `unverifiable`；action: `keep`(默认) | `remove` | `replace`(refs) | `drop_refs`(refs)；`move_to` 句子。
- 记录 id：`M<n>` = 原稿文献表第 n 条，`L<i>-<k>` = 第 i 个文献库的第 k 条（brief 里直接给出）；也可用原编号 `"7"` 或 BibTeX key。
- 句子：`u<unit>s<k>`，或 `"text:<句中一段原文>"`（跨运行稳定，推荐）。
- 只能引用输入里存在的文献；补字段必须写 `_source`（你实际读到的出处）。不新增材料外事实。

## 输出（/app/output）

| 文件 | 内容 |
|-|-|
| `<稿件名>_revised.<ext>` | 可继续编辑的稿件（与输入同格式；PDF 输入 → .md；.doc → .docx），docx 有 LibreOffice 时附 PDF/PNG 预览 |
| `references_<style>.txt`, `references.bib/.ris/.csl.json` | 同步后的文献表（目标规范）及导出 |
| `citation_map.json` | 每处引用：句子 id 与原文、旧→新标记、文献（编号/DOI/核验状态）、`verdict` + `verdict_source` + `match_basis`、PDF 证据（页码 + 原文摘录） |
| `merge_log.json`, `library_dedup.json` | 每对文献的去重判定（规则 + 理由）、簇、字段来源 |
| `verification.json` | 每条文献：verified / verified_with_corrections / verified_via_arxiv / verified_by_pdf / unverified_no_registry_match / not_found / doi_not_found / mismatch / unverified_offline，注册库值、更正、离线问题 |
| `renumber_map.json`, `manuscript.diff` / `manuscript_changes.md` | 旧号→新号；修改差异 |
| `review.md` | 人类可读报告 |
| `result.json` | `case_id`、全部契约字段（内容而非仅路径）、`status`(complete/partial/failed)、`status_reason`、`summary`、`changes`、`needs_review`、`consistency_check`、`contract_mapping`/`contract_unfilled`、`inputs`(sha256)、`uncertainty` |

`complete` 仅当：编号校验通过、无阻断项、无“needs_check/unverifiable”引用、无未处理的缺引用论断、无被删除的引用。

## 脚本做了什么

- **标记**：`[1]` `[1,3]` `[2-5]` `[1][2]` `［1］` `^[1]^` `<sup>[1]</sup>` `¹⁻³`（排除 m²/x² 等单位与公式）、docx 上标、`\cite{}`、`[@key]`、
  `(He et al., 2016a)`、`He et al. (2016)`、`（何恺明等，2016）`。图表注、附录按阅读顺序参与编号。
- **编号**（GB/T 顺序编码制）：首次出现顺序；同一标记内重复合并；`[1-3]` 压缩；统一标记样式；未被引用的条目移出并报告；
  找不到条目的标记生成醒目占位条目并报告。
- **位置**：段末堆叠引用若某来源明显对应前面某句则拆到该句（并记录）；目标句已引同一文献则不重复。带论断提示词
  （研究表明/已被证明/has been shown…）而无引用的句子列出，并按匹配度给出库内候选。
- **去重规则**（逐对记录）：D1 同 DOI（含中英文题名同一文章）、D2 同 arXiv id、D3 题名=另一条的译名、D4 规范化题名相同且第一作者相同、
  年份差 ≤2（预印本↔正式版）、D5 题名极相似 + 作者重合（合并但待确认）。不合并：G1 同 DOI 不同题名（DOI 错）、G2 同题名两个出版 DOI、
  G4 同题名年份差 >2（重印）、G3 同作者同年不同题名。正式版优先于预印本；簇内字段冲突（年/卷/期/页）报告并采用结构化文献库的值。
- **核验**：离线（必填字段、DOI 前缀与刊物、arXiv 年份、页码、ISBN）；在线 Crossref（DOI 查询、题名检索需题名 + 作者 + 年份同时吻合）、
  arXiv、预印本的正式版提示、注册库作者更全时补全；提供被引论文 PDF 时按 DOI/题名匹配到条目，逐句给出最匹配原文段落（页码 + 摘录），
  并检查是否另一篇提供的 PDF 明显更匹配（疑似错引）。
- **格式**：GB/T 7714-2015（[J] [C]// [M] [D] [R] [S] [P] [EB/OL]，arXiv 用 [J/OL] + arXiv 号，≤3 作者 + 等/et al，末尾 DOI）、APA 7（a/b 后缀）、
  BibTeX、RIS、CSL-JSON。目标规范缺的字段只报告，不猜。

## 异常处理

| 情况 | 行为 |
|-|-|
| case.json 缺失/损坏 | status failed + 原因；仍可用 `--manuscript/--library` 直接跑 |
| 稿件为 .pdf / .doc / .odt / .rtf | PDF 按文本层转为 .md（报告“版式未保留”）；其余用 LibreOffice 转 .docx；不可转时 failed + 原因 |
| BibTeX 括号不配、RIS 无 ER、未知格式 | 其余条目照常读入，问题列在 `parse_problems` |
| 无稿件只有文献库 | 去重 + 核验 + 转换，文献表含全部去重后条目 |
| 无文献表且无文献库 | failed + 原因 |
| PDF 加密/无文本层/匹配不到条目 | 报告原因；该条目只用元数据判断 |
| 网络不可用、429 限流 | 重试一次，随后 `unverified_offline` 并写明原因；运行照常完成 |
| docx 含 Word 域代码（EndNote/Zotero） | 改写为纯文本并在 status_reason 警告 |

## 局限

词项匹配只是线索：判断“句子结论是否真出自该文献”要读来源（有 PDF 时看 `evidence` 摘录）。拼音与中文姓名不自动对应。
很多会议论文/中文期刊在 Crossref 无记录，结果为 `unverified_no_registry_match` 而非“编造”。LaTeX 编号交给 BibTeX。

其他命令：`cite.py check --manuscript F`（任意编号稿件的一致性检查）、`cite.py convert --library L --to gbt7714|apa7|bibtex|ris|csl [--dedup]`、
`port_edits.py`（稿件变动后迁移 edits）。分步模式：`cite.py init` + `cite.py run ...`（参数同上）。
