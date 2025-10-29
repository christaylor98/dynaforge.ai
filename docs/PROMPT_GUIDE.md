# 🤖 Codex Prompt Guide

This guide defines how to interact with ChatGPT Codex or CLI assistants in this project.

---

## 1. GENERAL PROMPT STRUCTURE

Always follow this 3-layer pattern:

**Context → Intent → Constraints**

Example:
> Context: "We’re in exp_zscore_atr, testing z-score + ATR exits using NAS100 1h candles."  
> Intent: "Add parameter sweep logic for ATR multiplier."  
> Constraints: "Don’t modify core libraries; keep computation vectorized."

---

## 2. PHASE-AWARE PROMPTS

| Workflow Phase | Prompt Examples |
|----------------|-----------------|
| **Plan** | "Draft a new hypothesis for a volatility-based trailing stop experiment." |
| **Implement** | "Generate experiment.py to test adaptive ATR exit; config.yaml defines multiplier range." |
| **Run** | "Add CLI args for start_date and end_date to control backtest window." |
| **Evaluate** | "Compare metrics.json files from exp_zscore_atr and exp_mean_rev, and summarize in Markdown." |
| **Promote** | "Extract the reusable indicator logic from experiment.py into trading/core/indicators/atr.py." |

---

## 3. STYLE & QUALITY RULES

- Explain reasoning **before** writing code.
- Use docstrings for every public function or class.
- Use type hints everywhere.
- Keep imports organized (`stdlib`, `third-party`, then `local`).
- Output diffs or changed sections only when editing existing files.
- Prefer vectorized pandas/numpy operations over loops.

---

## 4. EXPERIMENT-SPECIFIC PROMPTS

Codex understands experiments better when prompted like this:

> "In this experiment, Sharpe < 0.3. Suggest three parameter variations that could improve it."

> "Plot rolling max-drawdown curve using results/trades.csv."

> "Summarize results from metrics.json into Markdown for inclusion in notes.md."

> "Create a function to merge all metrics.json files in trading/experiments/**/results into a comparison table."

---

## 5. DOCS & REPORTS PROMPTS

> "Update docs/ARCHITECTURE.md to include the new `eval/` submodule."  
> "Generate a report comparing all experiments tagged as release-candidate."  
> "Explain the rationale behind the Z-Score + ATR method for new readers."

---

## 6. EXPERIMENT CREATION PROMPT

> "Follow project workflow Phase 2. Create a new experiment named exp_mean_rev_vol targeting mean-reversion using volatility filters. Include template files and starter code."

---

## 7. TESTING PROMPTS

> "Write pytest tests for trading/core/metrics.py ensuring sharpe_ratio and max_drawdown behave as expected."  
> "Generate quick synthetic OHLCV data for testing experiment pipelines."

---

## 8. TONE & OUTPUT STYLE

- Be concise, technical, and reproducible.
- Use Markdown for summaries, code blocks for examples.
- Prefer `poetry` and `pytest` commands when suggesting shell instructions.
