"""The tests that make the agent honest.

test_no_forbidden_features is the single most valuable test in this repo:
casual + registered == cnt exactly, so any model handed those columns
scores R^2 = 1.0 and looks brilliant while having learned nothing.
"""
import pandas as pd
import pytest

from src.config import FORBIDDEN, TARGET
from src.features import build_features, encode_weather, feature_columns
from src.ingest import load_raw


@pytest.fixture(scope="module")
def feats():
    return build_features(load_raw())


def test_leakage_identity_holds(feats):
    """Documents *why* casual and registered are forbidden."""
    assert (feats.casual + feats.registered == feats[TARGET]).all()


def test_no_forbidden_features(feats):
    """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
    construction, so this cannot discover a *new* leaky column. What it
    catches is someone editing feature_columns() or FORBIDDEN -- which is
    exactly the fault the Step 7 hook demonstrates."""
    cols = set(feature_columns(feats))
    assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"


def test_no_feature_copies_a_forbidden_column(feats):
    for candidate in set(feature_columns(feats)) - FORBIDDEN:
        for forbidden in FORBIDDEN & set(feats.columns):
            assert not feats[candidate].eq(feats[forbidden]).all(), (
                f"{candidate} copies forbidden column {forbidden}"
            )


def test_unknown_weather_is_rejected():
    with pytest.raises(ValueError, match="unmapped weather labels.*UNKNOWN"):
        encode_weather(pd.Series(["GOOD", "UNKNOWN"]))


def test_lags_are_true_calendar_lags(feats):
    """cnt_lag_1 for date d must equal cnt on d-1, in calendar days."""
    by_date = feats.set_index("dteday")[TARGET]
    checked = 0
    for date, lag in feats.set_index("dteday").cnt_lag_1.items():
        prev = date - pd.Timedelta(days=1)
        if prev in by_date.index:
            assert lag == pytest.approx(by_date[prev]), f"bad lag at {date.date()}"
            checked += 1
    assert checked > 600, "too few rows actually verified"


def test_lag_is_not_the_target(feats):
    assert not (feats.cnt_lag_1 == feats[TARGET]).all()


def test_rolling_mean_excludes_today(feats):
    """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
    by_date = feats.set_index("dteday")[TARGET]
    date = feats.dteday.iloc[200]
    window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
    if all(d in by_date.index for d in window):
        expected = sum(by_date[d] for d in window) / 7
        assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)


def test_roll_range_7_excludes_today(feats):
    """cnt_roll_range_7 must be max-min of the 7 calendar days *before* today.

    Expected value is hand-computed, independent of the feature code: the raw
    counts for 2011-03-11 .. 2011-03-17 are 1977, 2132, 2417, 2046, 2056,
    2192, 2744, so the trailing 7-day range on 2011-03-18 is 2744 - 1977 = 767.
    """
    if "cnt_roll_range_7" not in feature_columns(feats):
        pytest.fail("cnt_roll_range_7 is missing from the model feature list")
    got = feats.set_index("dteday").cnt_roll_range_7.get(pd.Timestamp("2011-03-18"))
    assert got is not None, "no row for 2011-03-18 in feature table"
    assert got == pytest.approx(767), f"cnt_roll_range_7 on 2011-03-18 is {got}, expected 767"


def test_no_missing_values(feats):
    assert feats[feature_columns(feats)].isna().sum().sum() == 0


def test_dates_are_sorted_and_unique(feats):
    assert feats.dteday.is_monotonic_increasing
    assert feats.dteday.is_unique
