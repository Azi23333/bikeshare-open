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
