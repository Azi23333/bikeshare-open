# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

- 2026-11-23 — Tested `cnt_roll_range_7` to measure recent demand variation. Its inputs are complete daily counts from the seven calendar days before the forecast date. On 182 H1 2012 validation days, ridge changed by +0.0712 R² and −122.6 MAE, and HGB changed by −0.1474 R² and +105.7 MAE. Both baselines were unchanged. The before and after validation results are saved in `reports/`.
- 2026-11-23 — Kept the starter's `CLAUDE.md` because its calendar alignment, shift-before-aggregation, and feature test requirements already cover this feature.
- 2026-11-23 — Kept `cnt_roll_range_7` because ridge, the stronger model on validation, cleared the 0.01 R² improvement threshold and reduced MAE. The comparison records the effect on both models.

### Exercise 1 attribution

Claude Code 2.1.325 with `glm-5.3-flash` via Ollama Cloud used `/new-feature`
to write and run the initial test and implement the feature. The `gpt-oss:20b`
connection probe ended at HTTP 402. Codex set up the environment, proposed the
feature, tightened the model-input assertion, simplified the rolling code,
verified both checkpoints, recorded the failure, and ran the validation comparison.
The student approved the feature experiment and decided to keep the feature.

### Exercise 2 decisions

- 2026-11-23 — Classified the raw columns in `src/config.py` so an unexpected header requires review. Added checks for exact copies of excluded columns and for unknown weather labels so those failures reach the test suite.
- 2026-11-23 — Updated `CLAUDE.md` with `/seed-fault` and the raw-column rule so future agent runs can reproduce the break, test, and repair cycle.
- 2026-11-23 — Added a SHA-256 check to `make data` because a shell copy could replace the dataset while passing the shape check. Pinned the CSV checkout bytes in `.gitattributes` so the same digest works across Git line-ending settings.
