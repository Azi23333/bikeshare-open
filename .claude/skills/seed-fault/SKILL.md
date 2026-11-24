---
name: seed-fault
description: Run one bikeshare verification experiment by seeding a small source-code fault, capturing the test and hook results, and restoring the code.
---

# Seed one fault

Use `$ARGUMENTS` to select the fault and the matching test.

| Case | Temporary change in `src/features.py` | Test in `tests/test_leakage.py` |
| --- | --- | --- |
| `forbidden-column` | Append `casual` to the output of `feature_columns()`. | `test_no_forbidden_features` |
| `rolling-shift` | Remove `.shift(1)` from `cnt_roll_7` only. | `test_rolling_mean_excludes_today` |
| `weather-raise` | Replace the `raise ValueError(...)` in `encode_weather()` with `pass`. | `test_unknown_weather_is_rejected` |

For an unclear argument, ask which case to run. Work on one case per session.

1. Read the target code and remember the exact lines to restore. Use Edit for the temporary change so `PostToolUse` can run.
2. Check what the hook reports, then run `python -m pytest tests/test_leakage.py::<test> -q --tb=short` while the fault is present. Keep the real failure and hook output in the transcript.
3. Use Edit to restore the original lines. Run the same test again and check the repair hook result. Restore the code even if a test or hook behaves unexpectedly.
4. Report the exact change, observed hook result, test outcomes, and repair actions. The operator can copy the evidence and count model turns from the transcript.

Keep changes confined to the temporary source edit. Preserve the raw CSV and the existing tests and hooks. Leave commits and evaluation runs to the operator.
