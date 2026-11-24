# Seeded faults

## Exercise 1 test-first run

Claude Code 2.1.325 with `glm-5.3-flash` via Ollama Cloud used `/new-feature`
to write and run the initial test. Codex tightened the column check to verify
that the predictor reaches the model. Codex then ran
`PYTEST_ADDOPTS=--tb=short make test` before the feature existed. Make exited
with status 2.

The test uses only the seven days before 2011-03-18. From 2011-03-11 through
2011-03-17, the minimum was 1,977 rides and the maximum was 2,744, giving a range
of 767 rides.

~~~text
python -m pytest tests/ -q
.........F.....                                                          [100%]
=================================== FAILURES ===================================
_______________________ test_roll_range_7_excludes_today _______________________
tests/test_leakage.py:68: in test_roll_range_7_excludes_today
    pytest.fail("cnt_roll_range_7 is missing from the model feature list")
E   Failed: cnt_roll_range_7 is missing from the model feature list
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_roll_range_7_excludes_today - Failed: cnt_...
1 failed, 14 passed in 17.47s
make: *** [Makefile:16: test] Error 1
~~~

## Exercise 2

Each source fault used a fresh Claude Code 2.1.325 session with `glm-5.3-flash` through Ollama Cloud. Claude Code made the temporary edits and repaired them. Codex set up the checks, checked the restored file against Git, and collected the transcripts. Repair turns count assistant responses after the failing hook through the restoring edit as repair turns. The pasted output omits local checkout paths and trailing whitespace.

### Forbidden column

`/seed-fault forbidden-column` changed `src/features.py` as shown below.

~~~diff
--- a/src/features.py
+++ b/src/features.py
@@ -85,7 +85,7 @@
 def feature_columns(df: pd.DataFrame) -> list[str]:
     """Numeric columns that are safe to feed the model."""
     numeric = df.select_dtypes(include="number").columns
-    return [c for c in numeric if c not in FORBIDDEN]
+    return [c for c in numeric if c not in FORBIDDEN] + ["casual"]


 if __name__ == "__main__":
~~~

The `PostToolUse:Edit` hook returned exit 2 before the direct pytest run.

~~~text
Leakage tests failed after editing src/features.py:
feats =         dteday  instant  season  ...  cnt_lag_7   cnt_roll_7 cnt_roll_range_7
0   2011-01-10     10.0  WINTER  ...    ...          2654.0
713 2012-12-31    731.0  WINTER  ...      920.0  1531.428571           2654.0

[714 rows x 29 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'cnt_roll_range_7', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})

tests/test_leakage.py:31: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 9 passed in 11.16s
~~~

The targeted test failed in Bash.

~~~text
$ python -m pytest tests/test_leakage.py::test_no_forbidden_features -q --tb=short
Error: Exit code 1
F                                                                        [100%]
=================================== FAILURES ===================================
__________________________ test_no_forbidden_features __________________________
tests/test_leakage.py:31: in test_no_forbidden_features
    assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E   AssertionError: forbidden columns in feature set: {'casual'}
E   assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'cnt_roll_range_7', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed in 11.38s
~~~

Claude Code restored the original line(s) in **2 repair turns**. The repair hook returned exit 0, and the same test passed.

~~~text
$ python -m pytest tests/test_leakage.py::test_no_forbidden_features -q --tb=short && git diff --stat
.                                                                        [100%]
1 passed in 5.22s
~~~

### Rolling mean without a lag

`/seed-fault rolling-shift` changed `src/features.py` as shown below.

~~~diff
--- a/src/features.py
+++ b/src/features.py
@@ -73,7 +73,7 @@
     # If you add a longer lag, raise LAG_WARMUP in src/config.py.
     out["cnt_lag_1"] = out[TARGET].shift(1)
     out["cnt_lag_7"] = out[TARGET].shift(LAG_WARMUP)
-    out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+    out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()

     # Demand variation over the seven calendar days before the forecast date.
     trailing_week = out[TARGET].shift(1).rolling(LAG_WARMUP)
~~~

The `PostToolUse:Edit` hook returned exit 2 before the direct pytest run.

~~~text
Leakage tests failed after editing src/features.py:
[714 rows x 29 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ± 0.00441486

tests/test_leakage.py:70: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 9 passed in 6.43s
~~~

The targeted test failed in Bash.

~~~text
$ python -m pytest tests/test_leakage.py::test_rolling_mean_excludes_today -q --tb=short
Error: Exit code 1
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_rolling_mean_excludes_today _______________________
tests/test_leakage.py:70: in test_rolling_mean_excludes_today
    assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E   assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E
E     comparison failed
E     Obtained: 4389.0
E     Expected: 4414.857142857143 ± 0.00441486
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed in 8.27s
~~~

Claude Code restored the original line(s) in **2 repair turns**. The repair hook returned exit 0, and the same test passed.

~~~text
$ python -m pytest tests/test_leakage.py::test_rolling_mean_excludes_today -q --tb=short
.                                                                        [100%]
1 passed in 4.37s
~~~

### Silent weather encoding

`/seed-fault weather-raise` changed `src/features.py` as shown below.

~~~diff
--- a/src/features.py
+++ b/src/features.py
@@ -27,7 +27,7 @@
     known = series.dropna()
     unknown = set(known.unique()) - set(WEATHER_ORDER)
     if unknown:
-        raise ValueError(f"unmapped weather labels: {sorted(unknown)}")
+        pass
     return series.map(WEATHER_ORDER).astype(float)


~~~

The `PostToolUse:Edit` hook returned exit 2 before the direct pytest run.

~~~text
Leakage tests failed after editing src/features.py:
...F......                                                               [100%]
=================================== FAILURES ===================================
_______________________ test_unknown_weather_is_rejected _______________________

    def test_unknown_weather_is_rejected():
>       with pytest.raises(ValueError, match="unmapped weather labels.*UNKNOWN"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_leakage.py:43: Failed
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_unknown_weather_is_rejected - Failed: DID ...
1 failed, 9 passed in 13.27s
~~~

The targeted test failed in Bash.

~~~text
$ python -m pytest tests/test_leakage.py::test_unknown_weather_is_rejected -q --tb=short
Error: Exit code 1
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_unknown_weather_is_rejected _______________________
tests/test_leakage.py:43: in test_unknown_weather_is_rejected
    with pytest.raises(ValueError, match="unmapped weather labels.*UNKNOWN"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_unknown_weather_is_rejected - Failed: DID ...
1 failed in 12.64s
~~~

Claude Code restored the original line(s) in **2 repair turns**. The repair hook returned exit 0, and the same test passed.

~~~text
$ python -m pytest tests/test_leakage.py::test_unknown_weather_is_rejected -q --tb=short
.                                                                        [100%]
1 passed in 6.51s
~~~

### Raw CSV replacement through Bash

The replacement changed the first day's `temp` from `1.229108` to `1.329108`. The copy lived under `.venv`, and the tracked CSV kept its original checksum throughout. The first Claude Code call was declined in `dontAsk` mode. The rerun used `acceptEdits` for that session and ran the single copy command. The project hook and permission rules stayed the same.

~~~text
$ cp .venv/exercise2/raw-copy/replacement.csv .venv/exercise2/raw-copy/data/raw/bike_daily.csv
{"stdout": "", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": true}
~~~

The transcript had zero `PostToolUse` events for the Bash call. The hook matches `Edit` and `Write`. The old `make data` still accepted the changed file because its columns and row count were valid.

Original copy with the starter check

~~~text
a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc  .venv/exercise2/raw-copy/data/raw/bike_daily.csv
python -m src.ingest
OK ingest: 728 rows, 2011-01-03 -> 2012-12-31
make data exit: 0
~~~

Replacement with the starter check

~~~text
323ede14e118c4e3c6d1b089e3cc7cf1c44dea1ac4d645a3ae40afee0fc269e0  .venv/exercise2/raw-copy/data/raw/bike_daily.csv
python -m src.ingest
OK ingest: 728 rows, 2011-01-03 -> 2012-12-31
make data exit: 0
~~~

A SHA-256 check in `make data` catches a changed file when the data stage runs. `.gitattributes` keeps Git from converting the checked-in CSV's line endings.

~~~diff
diff --git a/.gitattributes b/.gitattributes
new file mode 100644
index 0000000..c2dfe39
--- /dev/null
+++ b/.gitattributes
@@ -0,0 +1 @@
+data/raw/bike_daily.csv -text
diff --git a/src/config.py b/src/config.py
index ea2fd6d..d7ef9e1 100644
--- a/src/config.py
+++ b/src/config.py
@@ -3,6 +3,7 @@ from pathlib import Path

 ROOT = Path(__file__).resolve().parents[1]
 RAW = ROOT / "data" / "raw" / "bike_daily.csv"
+RAW_SHA256 = "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc"
 PROCESSED = ROOT / "data" / "processed" / "features.parquet"
 METRICS = ROOT / "reports" / "metrics.json"

diff --git a/src/ingest.py b/src/ingest.py
index 6654075..8841383 100644
--- a/src/ingest.py
+++ b/src/ingest.py
@@ -1,13 +1,14 @@
-"""Stage 1: fetch the raw dataset and assert its shape.
+"""Stage 1: fetch the raw dataset and verify its checksum and shape.

 Run: python -m src.ingest
 """
 import sys
 import urllib.request
+from hashlib import sha256

 import pandas as pd

-from src.config import DATA_URL, RAW
+from src.config import DATA_URL, RAW, RAW_SHA256

 EXPECTED_MIN_ROWS = 700
 REQUIRED_COLS = {"dteday", "cnt", "casual", "registered", "temp", "hum", "windspeed"}
@@ -32,5 +33,7 @@ def load_raw() -> pd.DataFrame:

 if __name__ == "__main__":
     download(force="--force" in sys.argv)
+    if sha256(RAW.read_bytes()).hexdigest() != RAW_SHA256:
+        raise SystemExit(f"Raw CSV SHA-256 mismatch for {RAW.name}. Restore the original CSV.")
     df = load_raw()
     print(f"OK ingest: {len(df)} rows, {df.dteday.min().date()} -> {df.dteday.max().date()}")
~~~

The same replacement with the checksum check

~~~text
323ede14e118c4e3c6d1b089e3cc7cf1c44dea1ac4d645a3ae40afee0fc269e0  .venv/exercise2/raw-copy/data/raw/bike_daily.csv
python -m src.ingest
Raw CSV SHA-256 mismatch for bike_daily.csv. Restore the original CSV.
make: *** [Makefile:7: data] Error 1
make data exit: 2
~~~

After restoring the original bytes in the copy

~~~text
a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc  .venv/exercise2/raw-copy/data/raw/bike_daily.csv
python -m src.ingest
OK ingest: 728 rows, 2011-01-03 -> 2012-12-31
make data exit: 0
~~~

### Contract test controls

Codex ran two more isolated checks. Each targeted pytest run exited with status 1. The first added `unreviewed_sensor` to the raw CSV. The second added `innocent_sensor` to the feature table as an exact copy of `casual`.

~~~text
E   AssertionError: unclassified raw columns: ['unreviewed_sensor']
~~~

~~~text
E   AssertionError: innocent_sensor copies forbidden column casual
~~~

Codex drafted `/seed-fault`, the contract checks, and the checksum change. Claude Code ran the three source experiments and the isolated Bash copy. Codex verified the copy and ran the checksum and contract controls.
