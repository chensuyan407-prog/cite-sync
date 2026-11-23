# cite-sync — ARM bundle for 写作04｜参考文献与引用管理 (product-arena-03-429cc14d)

`submission/` is the Skill the platform installs (`SKILL.md` + `scripts/` + docs + a minimal example).
Everything else is the evidence for this attempt.

| path | content |
|-|-|
| `submission/` | Skill: SKILL.md, scripts (Python stdlib, python-docx for .docx), README (method, rules, mapping tables, limits), examples |
| `skills/SKILL.md` | copy of the Skill entry file (ARM layout) |
| `src/reproduce.py` | runs the whole self-evaluation and rewrites `execution/`, `trace/`, `characterization.json`, `arm_manifest.json` |
| `tests/cases/*/input` | author's cases: `zh_review` (GB/T, md, bib + RIS + CNKI enw), `zh_docx` (same as docx with superscripts), `en_apa` (author-year), `holdout_gnn` (written after the code freeze), `en_tex` (LaTeX keys) |
| `tests/cases/*/truth.json` | planted defects and the checks scored on the written files |
| `tests/cases/*/edits_agent.json` | the judgement step (verdicts / additions / removal) written as the agent would |
| `tests/run_eval.py` | scoring + baselines B0 (untouched) and B1 (regex renumber only) |
| `tests/FREEZE_holdout.sha256` | script hashes before the first held-out run |
| `execution/run.log`, `execution/results/` | log, `metrics.json`, `eval_rows.json`, per-case outputs, robustness runs |
| `trace/trace.jsonl` | tool calls of the reproduction run |

Run: `pip install python-docx` then `python src/reproduce.py` (online by default; `--offline` skips Crossref/arXiv; the
online checks Z16/Z18–Z20 then fail by design). All references in the cases are real works. One planted entry
(`Smith & Brown 2019`, DOI `10.1038/s41586-019-9999-9`) is fabricated on purpose to test detection.

Results (see `execution/results/metrics.json`): dev 60 checks, held-out 14 pre-registered checks plus 2 added after
the freeze, 8 robustness checks. The platform's fixed cases and its base-agent comparison are not reproduced here.
