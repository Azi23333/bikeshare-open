# Peer audit

- Repository [kyleduongg/bikeshare-open](https://github.com/kyleduongg/bikeshare-open)
- Reviewed commit [`a8e71ef76bbd38dcabfe79af4f5b375a6dcb5a08`](https://github.com/kyleduongg/bikeshare-open/commit/a8e71ef76bbd38dcabfe79af4f5b375a6dcb5a08)
- Review date 2026-11-23
- Auditor `/leakage-auditor`, run with `claude --agent leakage-auditor` in Claude Code 2.1.325 using `glm-5.3-flash` via Ollama Cloud

## Auditor output

~~~~text
All five checks pass for the production path (`src/ingest.py` → `src/features.py` → `src/train.py`, which is the only thing `make all` runs and the only writer of `reports/metrics.json`).

1. **Target leakage** — `casual`/`registered`/`cnt` and time-index columns are excluded via `FORBIDDEN` (`src/config.py:31-52`), and `feature_columns()` (`src/features.py:82-88`) filters by that set rather than hand-typing. No arithmetic combination of the target exists outside the explicitly-lagged features (`cnt_lag_1/2/7`, `cnt_roll_7`), and `cnt_roll_7` is `shift(1).rolling(7)` (`src/features.py:77`), so today's count never enters a feature.
2. **Temporal ordering** — every lag/rolling aggregand is `.shift(1)`-shifted or pure-shifted before aggregation; `temporal_split` splits by date (`src/train.py:59-61`); the only fitted transformer (StandardScaler in the ridge pipeline) is fit inside `model.fit(train[cols], ...)` at `src/train.py:78` and only ever sees train rows. The persistence baseline fits nothing.
3. **Calendar gaps** — `reindex_to_calendar` (`src/features.py:34-50`) builds the gap-free daily index *before* any lag is computed; `tests/test_leakage.py:34-43` verifies calendar-day lags by date and `tests/test_contract.py:22-25` verifies the reindexed grid is contiguous.
4. **Silent row loss** — the post-lag `.dropna()` (`src/features.py:79`) has no inline assertion, but `tests/test_contract.py:28-43` bounds the loss to `LAG_WARMUP + LAG_WARMUP × missing_days` (exact for this data: 14 rows for the single 2011-03-10 gap), and `encode_weather` raises on unmapped labels instead of producing silent NaNs (`src/features.py:28-30`). No row-loss defect for this run.
5. **Baselines** — `baseline_mean` (DummyRegressor) and `baseline_persistence` (cnt_lag_1) are both in `MODELS` (`src/train.py:48-53`) and score every split next to ridge and hgb, guarded by `tests/test_contract.py:55-58`.

Separately noted, not a production defect: `experiments/target_difference.py` is a deliberately leaky-style reconstruction (predicts the residual on `cnt_lag_1` then adds it back), but it discards the test split, evaluates on validation only, and does not write `metrics.json` or get invoked by the Makefile. `src/leakage_demo.py` is likewise not wired into the pipeline.

No findings — the production pipeline passes all five checks under static review; no code was executed, so row-loss counts and split sizes are reasoned, not run.
~~~~

## My verdict

I agree that the static review found no issue that changes the default pipeline's results. The code uses past demand for lags, fits the models on the training dates, and scores both baselines on each split. The separate validation experiment uses yesterday's actual count to reconstruct the forecast. That count is already available in a one-day-ahead setup, so the reconstruction is valid under that setup. The experiment runs separately from `make all`.
