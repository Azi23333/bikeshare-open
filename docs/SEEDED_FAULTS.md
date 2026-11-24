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

I ran each source fault in a fresh Claude Code 2.1.325 session with `glm-5.3-flash` through Ollama Cloud. Claude Code made the temporary edits and repaired them. Codex set up the checks, checked the restored file against Git, and collected the transcripts. I count assistant responses after the failing hook through the restoring edit as repair turns. The pasted output omits local checkout paths and trailing whitespace.

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
