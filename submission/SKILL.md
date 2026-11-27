---
name: cite-sync
description: 参考文献与引用管理 / citation & reference-list management. Use for a manuscript (.md/.txt/.docx/.tex, also .pdf/.doc) and/or reference libraries (BibTeX, RIS, EndNote/CNKI .enw, NoteExpress, CSL-JSON, numbered lists) when the task asks to insert/place citations, renumber [n] after edits, sync text numbers with the reference list, de-duplicate entries (zh/en titles, preprint vs published), convert to GB/T 7714-2015 / APA 7 / BibTeX / RIS, or verify references and claim-source match. One command writes the revised manuscript, the synced reference list and a complete result.json.
---

# cite-sync v0.2.1

脚本一步完成全部确定性工作（去重、核验、插入/重排编号、文献表同步、格式转换、契约字段填充、写后一致性复查）。你只需运行、看结果、必要时做一次判断。

## 步骤（通常 3–5 轮请求）

1. **运行主命令**（5–40 s；在线核验总预算 20 s，无网络自动离线，不会卡住）：
   ```bash
   PY=$(command -v python3 || command -v python)
   for d in /skills/weekly-skill /app/submission /app/skills "$(pwd)"; do [ -f "$d/scripts/cite.py" ] && S="$d" && break; done
   "$PY" "$S/scripts/cite.py" auto --case /input/case.json --out /app/output --work /app/work
   ```
   结果已全部写入 `/app/output`（含 `result.json`），这一步之后就是合法、完整的交付。
2. **读 `/app/work/brief.md`**（很短）。若写着 *Nothing to decide*，或 `result.json` 的 `status` 为 `success`，**直接结束**。
3. **仅当 brief 列出待判断项时**（可选，一轮即可）：
   ```bash
   cp /app/work/edits_draft.json /app/work/edits.json
   ```
   把其中 `<...>` 占位换成你的判断：引用 → `supported` / `partial` / `mismatch` / `unverifiable` 加一句 `note`；
   缺引用论断 → `supported`（插入建议文献）或 `reject`（留给作者）。没把握的条目保持占位即可（会被跳过，不报错）。
   然后带 `--edits /app/work/edits.json` 再跑一次第 1 步的命令。
4. 不要手改 result.json 里的编号/文献表；不要编造来源或字段。

自动选错文件时可加：`--manuscript F --library L --pdf P --style gbt7714|apa7`；强制离线加 `--offline`。

## 最短正例

输入：`examples/input/manuscript.md`（`…识别的性能[2]。…梯度消失问题。…循环结构[1][3]。` + 文末 3 条）+ `library.bib`（Attention 的 NeurIPS 正式版）。
```bash
python3 scripts/cite.py auto --case examples/input/case.json --out /tmp/out --work /tmp/work
```
示意输出（示例，非正式结果）：编号按首次出现重排为 `[1]…[2]…[3]`，段末 `[1][3]` 中的 LSTM 文献移到它支撑的句子；
预印本 `[3]` 与库中正式版按 `D4` 合并并改为 `[C]//Advances in Neural Information Processing Systems, 2017: 5998-6008`；`"status": "success"`。

## 输出（/app/output）

| 文件 | 内容 |
|-|-|
| `<稿件名>_revised.<ext>` | 可继续编辑的稿件（同输入格式；PDF→.md），docx 附 PDF 预览 |
| `references_<style>.txt`, `references.bib/.ris/.csl.json` | 同步后的文献表与导出 |
| `result.json` | `case_id`、全部契约字段、`status`、`status_detail`（blocking/advisory）、`warnings`、`actions_coverage`（六类动作计数）、`changes`、`needs_review`、`consistency_check`、`uncertainty`、`inputs`(sha256) |
| `citation_map.json` | 每处引用：句子原文、旧→新标记、文献、核验状态、`verdict` + `match_basis`、PDF 页码与摘录 |
| `merge_log.json` | 每对文献的去重规则与理由（D1 同 DOI · D2 同 arXiv · D3 中英译名 · D4 同题同作者/预印本↔正式版 · D5 近似待确认；G1–G4 不合并） |
| `verification.json`, `renumber_map.json`, `manuscript.diff`, `review.md` | 逐条核验、旧号→新号、修改差异、人类可读报告 |

## status 含义

- `success`：稿件与文献表已写出且写后复查通过。查不到注册记录的中文/会议文献、离线运行、启发式判断、
  无合适文献的缺引论断、被你删除的引用等只记入 `warnings` / `needs_review`（`severity: advisory`），不影响 status。
- `partial`：仅限硬问题——编号/文献表复查失败、正文标记找不到条目、仍被引用的来源 DOI 不可解析/疑似编造、
  文献库里有合适文献但缺引论断尚未决定、去重冲突。原因写在 `status_detail.blocking`。
- `failed`：无可用稿件且无文献库、case.json 缺失、文件不可读（exit 2）。

## 异常处理

BibTeX 括号不配 / RIS 无 ER → 其余条目照常读入并列在 `parse_problems`；PDF 加密或无文本层 → 报告原因，按元数据判断；
网络不可用 / 429 → 首次失败即转 `unverified_offline` 并写明原因；docx 含 EndNote/Zotero 域代码 → 改为纯文本并警告；
edits.json 写得不规范（注释、尾逗号、同义词、旧编号作键、整句原文）→ 尽量容错解析，无法理解的条目跳过并记入 `parse_problems`。

## 局限

词项匹配只是线索，不等于读过原文；拼音与中文姓名不自动对应；LaTeX 编号交给 BibTeX。
其他命令：`cite.py check --manuscript F`（一致性检查）、`cite.py convert --library L --to gbt7714|apa7|bibtex|ris|csl [--dedup]`。
