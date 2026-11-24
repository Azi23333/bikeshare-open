# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

## Exercise 1

- 2026-11-23 — Approved testing `cnt_roll_range_7` to measure demand variation using complete daily counts from the seven calendar days before the forecast date. On 182 validation days in H1 2012, Ridge changed by +0.0712 R² and −122.6 MAE, and HGB changed by −0.1474 R² and +105.7 MAE. Both baselines were unchanged. [Before](../reports/exercise1_validation_before.json) · [After](../reports/exercise1_validation_after.json)
- 2026-11-23 — Kept the starter's `CLAUDE.md` for this exercise because its calendar alignment, shift-before-aggregation, and feature test rules already covered the new feature.
- 2026-11-23 — Kept `cnt_roll_range_7` because Ridge had the stronger validation performance, gained more than 0.01 R², and reduced MAE.

## Exercise 2

- 2026-11-23 — Classified raw columns in `src/config.py` so unexpected headers require review. Added tests for exact copies of excluded columns and for unknown weather labels.
- 2026-11-23 — Added `/seed-fault` and the raw-column rule to `CLAUDE.md` to make the fault, test, and repair sequence reproducible.
- 2026-11-23 — Added a SHA-256 check to `make data` after a replacement CSV passed the original shape check. Used `.gitattributes` to keep the CSV's bytes consistent across Git line-ending settings.
