import numpy as np
import pandas as pd
import pytest
from innovate.compete.competition import MultiProductDiffusionModel
from innovate.diffuse.bass import BassModel
from innovate.diffuse.gompertz import GompertzModel
from innovate.diffuse.logistic import LogisticModel
from innovate.fitters.scipy_fitter import ScipyFitter
from innovate.models.hierarchical import HierarchicalModel
from innovate.models.mixture import MixtureModel


# Fixture for common test data
@pytest.fixture()
def synthetic_data():
    time_points = np.arange(1, 51)
    # True parameters for Bass model
    true_p = 0.03
    true_q = 0.3
    true_m = 1000

    def _bass_cumulative_true(t, p, q, m):
        exp_term = np.exp(-(p + q) * t)
        return m * (1 - exp_term) / (1 + (q / p) * exp_term)

    cumulative_adoptions = _bass_cumulative_true(time_points, true_p, true_q, true_m)

    # Add some noise and ensure non-negativity and cumulativity
    np.random.seed(42)
    noise = np.random.normal(0, 10, len(time_points))
    observed_adoptions = cumulative_adoptions + noise
    observed_adoptions[observed_adoptions < 0] = 0
    observed_adoptions = np.maximum.accumulate(observed_adoptions)

    return time_points, observed_adoptions


# Test BassModel
def test_bass_model_fit_predict(synthetic_data):
    t, y = synthetic_data
    model = BassModel()
    fitter = ScipyFitter()
    fitter.fit(model, t, y)

    assert model.params_ is not None
    assert all(param in model.params_ for param in ["p", "q", "m"])
    assert model.params_["m"] > 0

    predictions = model.predict(t)
    assert len(predictions) == len(t)
    assert np.all(predictions >= 0)
    assert np.all(
        np.diff(predictions) >= -1e-6,
    )  # Ensure non-decreasing (allowing for small numerical errors)


def test_bass_model_score(synthetic_data):
    t, y = synthetic_data
    model = BassModel()
    fitter = ScipyFitter()
    fitter.fit(model, t, y)
    score = model.score(t, y)
    assert isinstance(score, float)
    assert (
        0.0 <= score <= 1.0
    )  # R^2 can be negative, but for good fits, it should be positive


# Test GompertzModel
def test_gompertz_model_fit_predict(synthetic_data):
    t, y = synthetic_data
    model = GompertzModel()
    fitter = ScipyFitter()
    fitter.fit(model, t, y)

    assert model.params_ is not None
    assert all(param in model.params_ for param in ["a", "b", "c"])
    assert model.params_["a"] > 0

    predictions = model.predict(t)
    assert len(predictions) == len(t)
    assert np.all(predictions >= 0)
    assert np.all(np.diff(predictions) >= -1e-6)


def test_gompertz_model_score(synthetic_data):
    t, y = synthetic_data
    model = GompertzModel()
    fitter = ScipyFitter()
    fitter.fit(model, t, y)
    score = model.score(t, y)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


# Test LogisticModel
def test_logistic_model_fit_predict(synthetic_data):
    t, y = synthetic_data
    model = LogisticModel()
    fitter = ScipyFitter()
    fitter.fit(model, t, y)

    assert model.params_ is not None
    assert all(param in model.params_ for param in ["L", "k", "x0"])
    assert model.params_["L"] > 0

    predictions = model.predict(t)
    assert len(predictions) == len(t)
    assert np.all(predictions >= 0)
    assert np.all(np.diff(predictions) >= -1e-6)


def test_logistic_model_score(synthetic_data):
    t, y = synthetic_data
    model = LogisticModel()
    fitter = ScipyFitter()
    fitter.fit(model, t, y)
    score = model.score(t, y)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


# Test MultiProductDiffusionModel
def test_multi_product_model_predict():
    p_vals = [0.02, 0.015]
    Q_matrix = [[0.3, 0.05], [0.03, 0.25]]
    m_vals = [1000, 800]
    product_names = ["ProdA", "ProdB"]

    model = MultiProductDiffusionModel(
        p=p_vals,
        Q=Q_matrix,
        m=m_vals,
        names=product_names,
    )
    time_horizon = np.arange(1, 101)
    predictions_df = model.predict(time_horizon)

    assert isinstance(predictions_df, pd.DataFrame)
    assert len(predictions_df) == len(time_horizon)
    assert list(predictions_df.columns) == product_names
    assert np.all(predictions_df.values >= 0)
    # Check if cumulative (each product's adoption should be non-decreasing)
    for col in product_names:
        assert np.all(np.diff(predictions_df[col].values) >= -1e-6)


def test_multi_product_model_score():
    p_vals = [0.02, 0.015]
    Q_matrix = [[0.3, 0.05], [0.03, 0.25]]
    m_vals = [1000, 800]
    product_names = ["ProdA", "ProdB"]

    model = MultiProductDiffusionModel(
        p=p_vals,
        Q=Q_matrix,
        m=m_vals,
        names=product_names,
    )
    time_horizon = np.arange(1, 101)
    predictions_df = model.predict(time_horizon)

    # Create dummy observed data for scoring
    observed_df = predictions_df * (1 + np.random.normal(0, 0.05, predictions_df.shape))
    observed_df[observed_df < 0] = 0
    # Ensure observed data is also cumulative for a fair comparison
    for col in observed_df.columns:
        observed_df[col] = np.maximum.accumulate(observed_df[col])

    score = model.score(time_horizon, observed_df)
    assert isinstance(score, float)
    # R^2 can be negative if the model is worse than a horizontal line
    # For a model predicting its own slightly noisy version, it should be high
    assert score > 0.5  # Expect a reasonably good score


# Test ScipyFitter
def test_scipy_fitter_single_model(synthetic_data):
    t, y = synthetic_data
    fitter = ScipyFitter()
    model = BassModel()

    # The ScipyFitter for Phase 1 just calls the model's fit method
    fitter.fit(model, t, y)

    assert model.params_ is not None
    assert all(param in model.params_ for param in ["p", "q", "m"])


def test_scipy_fitter_multi_product_model_working():
    """Test that ScipyFitter now works with MultiProductDiffusionModel."""
    fitter = ScipyFitter()
    p_vals = [0.02, 0.015]
    Q_matrix = [[0.3, 0.05], [0.03, 0.25]]
    m_vals = [1000, 800]
    model = MultiProductDiffusionModel(p=p_vals, Q=Q_matrix, m=m_vals)
    
    # Generate synthetic data for fitting
    time_points = np.arange(1, 20)
    # Create synthetic multi-product data
    true_model = MultiProductDiffusionModel(p=p_vals, Q=Q_matrix, m=m_vals)
    clean_data = true_model.predict(time_points)
    
    # Add small amount of noise
    np.random.seed(42)
    noisy_data = clean_data + np.random.normal(0, 10, clean_data.shape)
    noisy_data = np.maximum(0, noisy_data)  # Ensure non-negative
    
    # Test that fitting works without raising NotImplementedError
    try:
        fitter.fit(model, time_points, noisy_data.values)
        # If we get here, the fitting worked
        assert model.params_ is not None
        assert 'p' in model.params_
        assert 'Q' in model.params_
        assert 'm' in model.params_
        print("✅ ScipyFitter with MultiProductDiffusionModel works correctly")
    except Exception as e:
        # Any other exception is a real error
        raise AssertionError(f"ScipyFitter.fit() with MultiProductDiffusionModel failed: {e}")


def test_mixture_model():
    t = np.linspace(0, 50, 100)
    models = [LogisticModel(), LogisticModel()]
    weights = [0.5, 0.5]
    model = MixtureModel(models, weights)

    # Set some dummy parameters
    model.params_ = {
        "model_0_L": 100.0,
        "model_0_k": 0.1,
        "model_0_x0": 10.0,
        "model_1_L": 200.0,
        "model_1_k": 0.2,
        "model_1_x0": 15.0,
    }

    y = model.predict(t)
    assert len(y) == 100


def test_mixture_model_weighting():
    t = np.linspace(1, 4, 4)
    models = [LogisticModel(), LogisticModel()]
    weights = [0.6, 0.4]
    model = MixtureModel(models, weights)
    model.params_ = {
        "model_0_L": 50.0,
        "model_0_k": 0.1,
        "model_0_x0": 5.0,
        "model_1_L": 150.0,
        "model_1_k": 0.2,
        "model_1_x0": 8.0,
        "weight_0": 0.6,
        "weight_1": 0.4,
    }
    # compute expected weighted average
    m1 = LogisticModel()
    m1.params_ = {"L": 50.0, "k": 0.1, "x0": 5.0}
    m2 = LogisticModel()
    m2.params_ = {"L": 150.0, "k": 0.2, "x0": 8.0}
    expected = 0.6 * m1.predict(t) + 0.4 * m2.predict(t)
    np.testing.assert_allclose(model.predict(t), expected)


def test_mixture_model_api():
    models = [LogisticModel(), LogisticModel()]
    weights = [0.5, 0.5]
    model = MixtureModel(models, weights)

    names = [f"model_{i}_{p}" for i, m in enumerate(models) for p in m.param_names]
    names.extend([f"weight_{i}" for i in range(len(models))])
    assert model.param_names == names

    guesses = model.initial_guesses([0, 1], [0, 1])
    assert set(guesses.keys()) == set(names)

    bounds = model.bounds([0, 1], [0, 1])
    assert set(bounds.keys()) == set(names)


def test_hierarchical_model(monkeypatch):
    t = np.linspace(0, 50, 100)
    model = HierarchicalModel(BassModel(), ["group1", "group2"])

    # Set some dummy parameters
    model.params_ = {
        "global_p": 0.001,
        "global_q": 0.1,
        "global_m": 1000,
        "group1_p": 0.002,
        "group1_q": 0.2,
        "group1_m": 2000,
        "group2_p": 0.003,
        "group2_q": 0.3,
        "group2_m": 3000,
    }

    def _predict(self, t_vals, covariates=None):
        p = self._params["p"]
        q = self._params["q"]
        m = self._params["m"]
        exp_term = np.exp(-(p + q) * np.array(t_vals))
        return m * (1 - exp_term) / (1 + (q / p) * exp_term)

    monkeypatch.setattr(BassModel, "predict", _predict)

    y = model.predict(t)
    assert len(y) == 100


def test_hierarchical_model_interface():
    base = BassModel()
    model = HierarchicalModel(base, ["g1", "g2"])
    # verify DiffusionModel compliance
    expected_names = [f"global_{p}" for p in base.param_names]
    for g in ["g1", "g2"]:
        expected_names.extend([f"{g}_{p}" for p in base.param_names])

    assert model.param_names == expected_names

    guesses = model.initial_guesses(np.arange(3), np.arange(3))
    for name in expected_names:
        assert name in guesses
    for p in base.param_names:
        assert guesses[f"g1_{p}"] == 0.0


def test_hierarchical_model_group_behavior(monkeypatch):
    t = np.linspace(1, 3, 3)
    base = BassModel()
    model = HierarchicalModel(base, ["g1", "g2"])
    model.params_ = {
        "global_p": 0.01,
        "global_q": 0.1,
        "global_m": 100,
        "g1_p": 0.005,
        "g1_q": 0.02,
        "g1_m": 10,
        "g2_p": -0.002,
        "g2_q": -0.03,
        "g2_m": -5,
    }

    # manual computation using analytic Bass solution
    def _bass_cumulative_true(t, p, q, m):
        exp_term = np.exp(-(p + q) * t)
        return m * (1 - exp_term) / (1 + (q / p) * exp_term)

    m1_pred = _bass_cumulative_true(t, 0.015, 0.12, 110)
    m2_pred = _bass_cumulative_true(t, 0.008, 0.07, 95)
    expected = m1_pred + m2_pred

    def _predict(self, t_vals, covariates=None):
        p = self._params["p"]
        q = self._params["q"]
        m = self._params["m"]
        exp_term = np.exp(-(p + q) * np.array(t_vals))
        return m * (1 - exp_term) / (1 + (q / p) * exp_term)

    monkeypatch.setattr(BassModel, "predict", _predict)

    np.testing.assert_allclose(model.predict(t), expected)
