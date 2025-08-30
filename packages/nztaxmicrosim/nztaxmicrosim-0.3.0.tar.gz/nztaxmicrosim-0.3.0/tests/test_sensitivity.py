import numpy as np
import pandas as pd
import pytest

from src.sensitivity_analysis import (
    _get_nested,
    _set_nested,
    run_deterministic_analysis,
    run_probabilistic_analysis,
)


def dummy_tax(income: float, rates: list[float], thresholds: list[float], **kwargs) -> float:
    if income <= thresholds[0]:
        return income * rates[0]
    return thresholds[0] * rates[0] + (income - thresholds[0]) * rates[1]


def dummy_wff(df: pd.DataFrame, wff_params: dict[str, float], wagegwt: float, days: int) -> pd.DataFrame:
    df = df.copy()
    df["ent"] = wff_params["ftc1"] * df["weight"]
    return df


population = pd.DataFrame({"familyinc": [4000, 6000], "weight": [1, 2]})

baseline_params = {
    "wff": {"ftc1": 100},
    "tax_brackets": {"rates": [0.1, 0.2], "thresholds": [5000]},
}


def total_wff(wff_df: pd.DataFrame, tax_df: pd.DataFrame) -> float:
    return wff_df["ent"].sum()


def total_tax(wff_df: pd.DataFrame, tax_df: pd.DataFrame) -> float:
    return tax_df["tax"].sum()


def net_cost(wff_df: pd.DataFrame, tax_df: pd.DataFrame) -> float:
    return total_wff(wff_df, tax_df) - total_tax(wff_df, tax_df)


metrics = {
    "Total WFF Entitlement": total_wff,
    "Total Tax Revenue": total_tax,
    "Net Cost to Government": net_cost,
}


def test_run_deterministic_analysis_shape_and_impact():
    params_to_vary = ["wff.ftc1", "tax_brackets.rates.0"]
    results = run_deterministic_analysis(
        baseline_params.copy(),
        params_to_vary,
        0.1,
        population,
        metrics,
        dummy_wff,
        dummy_tax,
        n_jobs=1,
    )

    assert set(results) == set(metrics)
    for df in results.values():
        assert df.shape[0] == len(params_to_vary)
        assert set(df.columns) == {"parameter", "low_value", "high_value", "baseline", "impact"}
        np.testing.assert_allclose(df["impact"], df["high_value"] - df["low_value"])
        assert df["baseline"].dtype.kind in "fiu"


def test_get_nested():
    """Test the _get_nested function."""
    d = {"a": {"b": [10, 20]}}
    assert _get_nested(d, "a.b.0") == 10
    assert _get_nested(d, "a.b.1") == 20
    assert _get_nested(d, "a.b") == [10, 20]
    assert _get_nested(d, "a") == {"b": [10, 20]}


def test_set_nested():
    """Test the _set_nested function."""
    d = {"a": {"b": [10, 20]}}
    _set_nested(d, "a.b.0", 100)
    assert d["a"]["b"][0] == 100
    _set_nested(d, "a.b", [30, 40])
    assert d["a"]["b"] == [30, 40]


def test_run_deterministic_analysis_unsupported_metric():
    """Test that an unsupported metric raises a KeyError."""
    params_to_vary = ["wff.ftc1"]
    bad_metrics = {"bad": lambda wff_df, tax_df: 0}
    with pytest.raises(KeyError):
        run_deterministic_analysis(
            baseline_params.copy(),
            params_to_vary,
            0.1,
            population,
            bad_metrics,
            dummy_wff,
            dummy_tax,
        )


def test_run_probabilistic_analysis_unsupported_dist():
    """Test that an unsupported distribution raises an error."""
    param_dists = {"wff.ftc1": {"dist": "bad_dist"}}
    with pytest.raises(ValueError):
        run_probabilistic_analysis(
            param_dists,
            1,
            population,
            metrics,
            dummy_wff,
            dummy_tax,
            n_jobs=1,
        )


def test_run_probabilistic_analysis_shape():
    param_dists = {
        "wff.ftc1": {"dist": "norm", "loc": 100, "scale": 1},
        "tax_brackets.rates.0": {"dist": "uniform", "loc": 0.1, "scale": 0.01},
    }
    num_samples = 5
    results = run_probabilistic_analysis(
        param_dists,
        num_samples,
        population,
        metrics,
        dummy_wff,
        dummy_tax,
        n_jobs=1,
    )

    assert set(results) == set(metrics)
    for arr in results.values():
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (num_samples,)


def test_run_deterministic_analysis_values_self_contained():
    # Define dummy functions and data within the test
    def dummy_tax(income, rates, thresholds):
        if income <= thresholds[0]:
            return income * rates[0]
        return thresholds[0] * rates[0] + (income - thresholds[0]) * rates[1]

    def dummy_wff(df, wff_params, wagegwt, days):
        df = df.copy()
        df["ent"] = wff_params["ftc1"] * df["weight"]
        return df

    population = pd.DataFrame({"familyinc": [4000, 6000], "weight": [1, 2]})
    baseline_params = {
        "wff": {"ftc1": 100},
        "tax_brackets": {"rates": [0.1, 0.2], "thresholds": [5000]},
    }
    metrics = {"Total WFF Entitlement": lambda wff_df, tax_df: wff_df["ent"].sum()}
    params_to_vary = ["wff.ftc1"]

    results = run_deterministic_analysis(
        baseline_params,
        params_to_vary,
        0.1,
        population,
        metrics,
        dummy_wff,
        dummy_tax,
        n_jobs=1,
    )

    df = results["Total WFF Entitlement"]
    np.testing.assert_allclose(df["baseline"][0], 300)
    np.testing.assert_allclose(df["low_value"][0], 270)
    np.testing.assert_allclose(df["high_value"][0], 330)


def test_run_deterministic_analysis_values():
    params_to_vary = ["wff.ftc1"]
    results = run_deterministic_analysis(
        baseline_params.copy(),
        params_to_vary,
        0.1,
        population,
        {"Total WFF Entitlement": lambda wff_df, tax_df: total_wff(wff_df, tax_df)},
        dummy_wff,
        dummy_tax,
        n_jobs=1,
    )
    df = results["Total WFF Entitlement"]
    np.testing.assert_allclose(df["baseline"][0], 300)
    np.testing.assert_allclose(df["low_value"][0], 270)
    np.testing.assert_allclose(df["high_value"][0], 330)


def _test_get_nested():
    d = {"a": {"b": [1, 2, {"c": 3}]}}
    assert _get_nested(d, "a.b.0") == 1
    assert _get_nested(d, "a.b.2.c") == 3


def _test_set_nested():
    d = {"a": {"b": [1, 2, {"c": 3}]}}
    _set_nested(d, "a.b.0", 4)
    assert d["a"]["b"][0] == 4
    _set_nested(d, "a.b.2.c", 5)
    assert d["a"]["b"][2]["c"] == 5
