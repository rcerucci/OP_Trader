import pytest
from src.env.env_libs.observation_builder import ObservationBuilder

class DummyCalculator:
    def calculate(self, market_data, portfolio_data, context=None):
        return {"custom_feature": 42.0}

class DummyScaler:
    def transform(self, arr):
        return arr / 10.0

@pytest.fixture
def ob_builder(tmp_path):
    schema = ["open", "close", "custom_feature"]
    calc = DummyCalculator()
    scaler = DummyScaler()
    builder = ObservationBuilder(
        feature_schema=schema,
        calculators=[calc],
        scaler=scaler,
        logger=None,
        debug=True
    )
    return builder

def test_build_observation_valid(ob_builder):
    market_data = {"open": 10.0}
    portfolio_data = {"close": 11.0}
    context = None
    obs = ob_builder.build_observation(market_data, portfolio_data, context)
    assert set(obs.keys()) == {"open", "close", "custom_feature"}
    assert obs["open"] == pytest.approx(1.0)
    assert obs["close"] == pytest.approx(1.1)
    assert obs["custom_feature"] == pytest.approx(4.2)

def test_validate_features_missing():
    builder = ObservationBuilder(feature_schema=["x", "y"])
    obs = {"x": 1.0}
    assert not builder.validate_features(obs)

def test_validate_features_nan():
    builder = ObservationBuilder(feature_schema=["a"])
    obs = {"a": float('nan')}
    assert not builder.validate_features(obs)

def test_save_snapshot(tmp_path):
    builder = ObservationBuilder(feature_schema=["a", "b"])
    builder._last_snapshot = {"a": 1.0, "b": 2.0}
    builder.save_snapshot(path=str(tmp_path))
    files = list(tmp_path.iterdir())
    assert any("obs_snapshot" in f.name for f in files)

def test_reset(ob_builder):
    ob_builder._last_snapshot = {"x": 1.0}
    ob_builder.reset()
    assert ob_builder._last_snapshot is None
