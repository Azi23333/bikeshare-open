# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

## Exercise 1

- 2026-11-23 — I chose to test `cnt_roll_range_7` to see whether recent swings in demand help predict ridership. It takes the highest minus the lowest daily count from the seven calendar days before the forecast date. Across 182 validation days in the first half of 2012, Ridge's R² rose by 0.0712 and its MAE fell by 122.6 rides. HGB's R² fell by 0.1474 and its MAE rose by 105.7 rides. Both baselines stayed the same. [Before](../reports/exercise1_validation_before.json) · [After](../reports/exercise1_validation_after.json)
- 2026-11-23 — Exercise 1 used the starter's `CLAUDE.md` as written. It already required a gap-free calendar, shifting before aggregation, and a test for each new lag or rolling feature.
- 2026-11-23 — I kept `cnt_roll_range_7` because Ridge was the stronger model on validation. Its R² gain cleared the 0.01 threshold and its MAE was lower.

## Exercise 2

- 2026-11-23 — `src/config.py` lists the known raw columns so new headers get reviewed. The tests flag unclassified columns, exact copies of excluded columns, and unknown weather labels.
- 2026-11-23 — `CLAUDE.md` now points to `/seed-fault` for repeating the fault, test, and repair steps. It also says to classify raw columns before using them.
- 2026-11-23 — A replacement CSV passed the original shape check, so `make data` now checks the file's SHA-256 hash. `.gitattributes` keeps Git from changing the CSV's line endings on checkout.
